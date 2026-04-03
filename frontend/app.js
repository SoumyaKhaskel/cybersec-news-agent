// ─────────────────────────────────────────
// CONFIG — change to your Railway URL after deployment
// ─────────────────────────────────────────
const API_BASE_URL = "https://cybernewzsk.up.railway.app/";

const ARTICLES_PER_PAGE  = 20;
const AUTO_REFRESH_MS    = 5 * 60 * 1000; // 5 minutes

// ─────────────────────────────────────────
// STATE
// ─────────────────────────────────────────
let currentSeverity = "";
let currentSearch   = "";
let currentOffset   = 0;
let totalArticles   = 0;
let searchTimer     = null;

// ─────────────────────────────────────────
// DOM REFERENCES
// ─────────────────────────────────────────
const feedGrid      = document.getElementById("feed-grid");
const loadMoreWrap  = document.getElementById("load-more-wrap");
const loadMoreBtn   = document.getElementById("load-more-btn");
const emptyState    = document.getElementById("empty-state");
const errorState    = document.getElementById("error-state");
const loadingState  = document.getElementById("loading-state");
const lastUpdated   = document.getElementById("last-updated");
const searchInput   = document.getElementById("search-input");

const statTotal    = document.getElementById("stat-total");
const statCritical = document.getElementById("stat-critical");
const statHigh     = document.getElementById("stat-high");
const statMedium   = document.getElementById("stat-medium");
const statLow      = document.getElementById("stat-low");

// ─────────────────────────────────────────
// UTILITIES
// ─────────────────────────────────────────

function timeAgo(dateStr) {
  if (!dateStr) return "Unknown time";
  const date = new Date(dateStr);
  if (isNaN(date)) return "Unknown time";
  const diff = Math.floor((Date.now() - date.getTime()) / 1000);
  if (diff < 60)   return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400)return `${Math.floor(diff / 3600)}h ago`;
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
  loadingState.style.display = state === "loading" ? "block" : "none";
  emptyState.style.display   = state === "empty"   ? "block" : "none";
  errorState.style.display   = state === "error"   ? "block" : "none";
}

// ─────────────────────────────────────────
// RENDER ARTICLE CARD
// ─────────────────────────────────────────

function renderCard(article) {
  const severity   = escapeHtml(article.severity   || "Unknown");
  const title      = escapeHtml(article.title      || "No title");
  const source     = escapeHtml(article.source     || "Unknown");
  const attackType = escapeHtml(article.attack_type|| "");
  const summary    = escapeHtml(article.ai_summary || "Summary not available yet.");
  const url        = escapeHtml(article.url        || "#");
  const timeStr    = timeAgo(article.fetched_at);

  const sevClass   = severityBadgeClass(severity);
  const cardClass  = `article-card sev-${severity}`;

  return `
    <div class="${cardClass}">
      <div class="card-top">
        <div class="card-badges">
          <span class="badge ${sevClass}">${severity}</span>
          ${attackType ? `<span class="badge badge-attack">${attackType}</span>` : ""}
        </div>
        <span class="card-time">${timeStr}</span>
      </div>
      <div class="card-source">${source}</div>
      <div class="card-title">${title}</div>
      <div class="card-summary">${summary}</div>
      <a class="card-link" href="${url}" target="_blank" rel="noopener noreferrer">
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
    const res  = await fetch(`${API_BASE_URL}/stats`);
    if (!res.ok) return;
    const data = await res.json();

    statCritical.textContent = data.Critical || 0;
    statHigh.textContent     = data.High     || 0;
    statMedium.textContent   = data.Medium   || 0;
    statLow.textContent      = data.Low      || 0;
  } catch (e) {
    console.warn("Stats fetch failed:", e);
  }
}

// ─────────────────────────────────────────
// LOAD FEED
// ─────────────────────────────────────────

async function loadFeed(reset = false) {
  if (reset) {
    currentOffset = 0;
    feedGrid.innerHTML = "";
    loadMoreWrap.style.display = "none";
    showState("loading");
  }

  const params = new URLSearchParams({
    limit:  ARTICLES_PER_PAGE,
    offset: currentOffset,
  });

  if (currentSeverity) params.append("severity", currentSeverity);
  if (currentSearch)   params.append("search",   currentSearch);

  try {
    const res = await fetch(`${API_BASE_URL}/feed?${params}`);
    if (!res.ok) throw new Error(`API returned ${res.status}`);
    const data = await res.json();

    totalArticles = data.total || 0;
    const articles = data.articles || [];

    showState(null);

    if (articles.length === 0 && currentOffset === 0) {
      showState("empty");
      statTotal.textContent = 0;
      return;
    }

    feedGrid.insertAdjacentHTML("beforeend", articles.map(renderCard).join(""));
    statTotal.textContent = totalArticles;

    currentOffset += articles.length;

    // Show or hide Load More button
    if (currentOffset < totalArticles) {
      loadMoreWrap.style.display = "flex";
    } else {
      loadMoreWrap.style.display = "none";
    }

    // Update last-updated timestamp
    const now = new Date();
    lastUpdated.textContent = `Last updated: ${now.toLocaleTimeString()}`;

  } catch (e) {
    console.error("Feed fetch failed:", e);
    if (currentOffset === 0) {
      showState("error");
    }
  }
}

// ─────────────────────────────────────────
// EVENT LISTENERS
// ─────────────────────────────────────────

// Filter buttons
document.querySelectorAll(".filter-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentSeverity = btn.dataset.severity || "";
    loadFeed(true);
  });
});

// Search input with debounce
searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    currentSearch = searchInput.value.trim();
    loadFeed(true);
  }, 400);
});

// Load more button
loadMoreBtn.addEventListener("click", () => {
  loadFeed(false);
});

// ─────────────────────────────────────────
// INIT
// ─────────────────────────────────────────

async function init() {
  await loadStats();
  await loadFeed(true);

  // Auto-refresh every 5 minutes
  setInterval(async () => {
    await loadStats();
    if (currentOffset === ARTICLES_PER_PAGE) {
      // Only auto-refresh if user hasn't loaded more pages
      await loadFeed(true);
    }
  }, AUTO_REFRESH_MS);
}

init();
