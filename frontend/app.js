// ─────────────────────────────────────────
// CONFIG — your Railway backend URL
// ─────────────────────────────────────────
const API_BASE_URL = "https://cybernewzsk.up.railway.app";

const ARTICLES_PER_PAGE = 20;
const AUTO_REFRESH_MS   = 5 * 60 * 1000; // 5 minutes

// ─────────────────────────────────────────
// RETRY CONFIG — fixes the random fetch fail
// Railway free tier has cold starts (sleeps
// after ~10 min inactivity). These settings
// auto-retry silently so recruiters never
// see a broken page.
// ─────────────────────────────────────────
const RETRY_ATTEMPTS  = 4;
const RETRY_DELAY_MS  = 2000;   // 2s between retries
const FETCH_TIMEOUT_MS = 12000; // 12s timeout per request

// ─────────────────────────────────────────
// STATE
// ─────────────────────────────────────────
let currentSeverity = "";
let currentSearch   = "";
let currentOffset   = 0;
let totalArticles   = 0;
let searchTimer     = null;
let isFirstLoad     = true;

// ─────────────────────────────────────────
// DOM REFERENCES
// ─────────────────────────────────────────
const feedGrid     = document.getElementById("feed-grid");
const loadMoreWrap = document.getElementById("load-more-wrap");
const loadMoreBtn  = document.getElementById("load-more-btn");
const emptyState   = document.getElementById("empty-state");
const errorState   = document.getElementById("error-state");
const loadingState = document.getElementById("loading-state");
const lastUpdated  = document.getElementById("last-updated");
const searchInput  = document.getElementById("search-input");

const statTotal    = document.getElementById("stat-total");
const statCritical = document.getElementById("stat-critical");
const statHigh     = document.getElementById("stat-high");
const statMedium   = document.getElementById("stat-medium");
const statLow      = document.getElementById("stat-low");

// ─────────────────────────────────────────
// CORE: fetchWithRetry
// Every API call goes through here.
// On failure it waits and retries up to
// RETRY_ATTEMPTS times before giving up.
// ─────────────────────────────────────────
async function fetchWithRetry(url, attempt = 1) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timer);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    return res;

  } catch (err) {
    clearTimeout(timer);

    if (attempt < RETRY_ATTEMPTS) {
      console.warn(
        `[CyberFeed] Fetch failed (attempt ${attempt}/${RETRY_ATTEMPTS}): ${err.message}. ` +
        `Retrying in ${RETRY_DELAY_MS / 1000}s...`
      );
      // Update header to show retrying state so user knows something is happening
      if (lastUpdated) {
        lastUpdated.textContent =
          `Reconnecting... (attempt ${attempt + 1}/${RETRY_ATTEMPTS})`;
      }
      await sleep(RETRY_DELAY_MS);
      return fetchWithRetry(url, attempt + 1);
    }

    // All attempts exhausted — rethrow
    throw err;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ─────────────────────────────────────────
// UTILITIES
// ─────────────────────────────────────────
function timeAgo(dateStr) {
  if (!dateStr) return "Unknown";
  const date = new Date(dateStr);
  if (isNaN(date)) return "Unknown";
  const diff = Math.floor((Date.now() - date.getTime()) / 1000);
  if (diff < 60)    return `${diff}s ago`;
  if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

function severityBadgeClass(severity) {
  const map = {
    "Critical": "badge-critical",
    "High":     "badge-high",
    "Medium":   "badge-medium",
    "Low":      "badge-low",
  };
  return map[severity] || "badge-medium";
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function showState(state) {
  if (loadingState) loadingState.style.display = state === "loading" ? "block" : "none";
  if (emptyState)   emptyState.style.display   = state === "empty"   ? "block" : "none";
  if (errorState)   errorState.style.display   = state === "error"   ? "block" : "none";
}

// ─────────────────────────────────────────
// RENDER ARTICLE CARD
// ─────────────────────────────────────────
function renderCard(article) {
  const severity   = escapeHtml(article.severity    || "Unknown");
  const title      = escapeHtml(article.title       || "No title");
  const source     = escapeHtml(article.source      || "Unknown");
  const attackType = escapeHtml(article.attack_type || "");
  const summary    = escapeHtml(article.ai_summary  || "Summary not available yet.");
  const url        = escapeHtml(article.url         || "#");
  const timeStr    = timeAgo(article.fetched_at);

  const sevClass  = severityBadgeClass(severity);
  const cardClass = `article-card sev-${severity}`;

  return `
    <div class="${cardClass}">
      <div class="card-top">
        <div class="card-badges">
          <span class="badge ${sevClass}">${severity}</span>
          ${attackType
            ? `<span class="badge badge-attack">${attackType}</span>`
            : ""}
        </div>
        <span class="card-time">${timeStr}</span>
      </div>
      <div class="card-source">${source}</div>
      <div class="card-title">${title}</div>
      <div class="card-summary">${summary}</div>
      <a class="card-link"
         href="${url}"
         target="_blank"
         rel="noopener noreferrer">
        Read original &rarr;
      </a>
    </div>
  `;
}

// ─────────────────────────────────────────
// LOAD STATS
// ─────────────────────────────────────────
async function loadStats() {
  try {
    const res  = await fetchWithRetry(`${API_BASE_URL}/stats`);
    const data = await res.json();

    if (statCritical) statCritical.textContent = data.Critical || 0;
    if (statHigh)     statHigh.textContent     = data.High     || 0;
    if (statMedium)   statMedium.textContent   = data.Medium   || 0;
    if (statLow)      statLow.textContent      = data.Low      || 0;
  } catch (e) {
    console.warn("[CyberFeed] Stats unavailable:", e.message);
    // Non-fatal — feed can still show without stats
  }
}

// ─────────────────────────────────────────
// LOAD FEED
// ─────────────────────────────────────────
async function loadFeed(reset = false) {
  if (reset) {
    currentOffset = 0;
    if (feedGrid) feedGrid.innerHTML = "";
    if (loadMoreWrap) loadMoreWrap.style.display = "none";
    showState("loading");
  }

  const params = new URLSearchParams({
    limit:  ARTICLES_PER_PAGE,
    offset: currentOffset,
  });
  if (currentSeverity) params.append("severity", currentSeverity);
  if (currentSearch)   params.append("search",   currentSearch);

  try {
    const res  = await fetchWithRetry(`${API_BASE_URL}/feed?${params}`);
    const data = await res.json();

    totalArticles = data.total || 0;
    const articles = data.articles || [];

    showState(null);

    if (articles.length === 0 && currentOffset === 0) {
      showState("empty");
      if (statTotal) statTotal.textContent = 0;
      return;
    }

    if (feedGrid) {
      feedGrid.insertAdjacentHTML("beforeend", articles.map(renderCard).join(""));
    }
    if (statTotal) statTotal.textContent = totalArticles;

    currentOffset += articles.length;

    if (loadMoreWrap) {
      loadMoreWrap.style.display = currentOffset < totalArticles ? "flex" : "none";
    }

    const now = new Date();
    if (lastUpdated) {
      lastUpdated.textContent = `Last updated: ${now.toLocaleTimeString()}`;
    }

  } catch (e) {
    console.error("[CyberFeed] Feed fetch failed after all retries:", e.message);
    if (currentOffset === 0) {
      showState("error");
      // Update error message to be helpful and not alarming
      const errEl = document.getElementById("error-state");
      if (errEl) {
        errEl.innerHTML = `
          <p>Unable to reach the feed server right now.</p>
          <p style="font-size:12px; margin-top:6px;">
            The server may be waking up — this usually takes 10–20 seconds.
          </p>
          <button onclick="retryLoad()">Retry</button>
        `;
      }
    }
  }
}

// ─────────────────────────────────────────
// RETRY LOAD — called by the error button
// ─────────────────────────────────────────
function retryLoad() {
  loadStats();
  loadFeed(true);
}

// ─────────────────────────────────────────
// KEEP-ALIVE PING
// Railway free tier sleeps after ~10 min
// of inactivity. This pings /health every
// 8 minutes so the server stays awake while
// the dashboard is open.
// ─────────────────────────────────────────
async function keepAlive() {
  try {
    await fetch(`${API_BASE_URL}/health`, {
      signal: AbortSignal.timeout(5000)
    });
  } catch (_) {
    // Silent — keep-alive failures are not shown to user
  }
}

// ─────────────────────────────────────────
// EVENT LISTENERS
// ─────────────────────────────────────────
document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn")
      .forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentSeverity = btn.dataset.severity || "";
    loadFeed(true);
  });
});

if (searchInput) {
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      currentSearch = searchInput.value.trim();
      loadFeed(true);
    }, 400);
  });
}

if (loadMoreBtn) {
  loadMoreBtn.addEventListener("click", () => {
    loadFeed(false);
  });
}

// ─────────────────────────────────────────
// INIT
// ─────────────────────────────────────────
async function init() {
  await loadStats();
  await loadFeed(true);

  // Auto-refresh feed every 5 minutes
  setInterval(async () => {
    await loadStats();
    if (currentOffset === ARTICLES_PER_PAGE) {
      await loadFeed(true);
    }
  }, AUTO_REFRESH_MS);

  // Keep Railway server awake every 8 minutes
  setInterval(keepAlive, 8 * 60 * 1000);
}

init();
