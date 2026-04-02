import json
import logging
import os
import time
from groq import Groq, RateLimitError, APIError
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")



SYSTEM_PROMPT = (
    "You are a cybersecurity analyst. Analyse the article and return "
    "ONLY a valid JSON object. No explanation. No markdown code fences. "
    "No text before or after the JSON. Just the raw JSON."
)

def build_prompt(title, content):
    snippet = (content or "")[:1500]
    return f"""Article title: {title}

Article content:
{snippet}

Return this exact JSON — fill in real values, do not copy the placeholders:
{{
  "summary": "Two sentences max. Plain English. What happened and who is affected.",
  "severity": "Critical",
  "attack_type": "Ransomware",
  "cves": ["CVE-2024-XXXX"],
  "affected_products": ["Product Name"]
}}

Rules:
- severity must be one of: Critical, High, Medium, Low
- attack_type must be one of: Ransomware, Phishing, Zero-day, Data breach, Vulnerability, Malware, DDoS, Supply chain, Other
- cves: empty list [] if none mentioned
- affected_products: empty list [] if none mentioned"""

def tag_article(title, content, retries=3):
    prompt = SYSTEM_PROMPT + "\n\n" + build_prompt(title, content)
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            raw = raw.strip("```json").strip("```").strip()
            result = json.loads(raw)
            return result
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            time.sleep(2)
    return {"summary": "Failed", "severity": "Medium",
            "attack_type": "Other", "cves": [], "affected_products": []}

def tag_article(title, content, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": build_prompt(title, content)}
                ],
                max_tokens=400,
                temperature=0.1
            )

            raw = response.choices[0].message.content.strip()
            raw = raw.strip("```json").strip("```").strip()

            result = json.loads(raw)

            valid_severities  = {"Critical", "High", "Medium", "Low"}
            valid_attack_types = {
                "Ransomware", "Phishing", "Zero-day", "Data breach",
                "Vulnerability", "Malware", "DDoS", "Supply chain", "Other"
            }

            if result.get("severity") not in valid_severities:
                result["severity"] = "Medium"
            if result.get("attack_type") not in valid_attack_types:
                result["attack_type"] = "Other"
            if not isinstance(result.get("cves"), list):
                result["cves"] = []
            if not isinstance(result.get("affected_products"), list):
                result["affected_products"] = []

            logger.info(
                f"  [AI] {result['severity']} | {result['attack_type']} "
                f"| {title[:45]}..."
            )
            return result

        except json.JSONDecodeError as e:
            logger.warning(
                f"  [AI] JSON parse fail (attempt {attempt+1}/{retries}): {e}"
            )
            if attempt < retries - 1:
                time.sleep(2)

        except RateLimitError:
            wait = 60
            logger.warning(f"  [AI] Rate limit hit — waiting {wait}s")
            time.sleep(wait)

        except APIError as e:
            logger.error(f"  [AI] Groq API error: {e}")
            break

        except Exception as e:
            logger.error(f"  [AI] Unexpected error: {e}")
            break

    logger.warning(f"  [AI] All attempts failed for: {title[:50]}")
    return {
        "summary": "AI tagging failed — see logs.",
        "severity": "Medium",
        "attack_type": "Other",
        "cves": [],
        "affected_products": []
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    test_title   = "LockBit 3.0 exploits Citrix Bleed CVE-2023-4966 in healthcare attacks"
    test_content = """
    A new LockBit 3.0 ransomware campaign is actively exploiting CVE-2023-4966,
    a critical Citrix NetScaler vulnerability. Over 50 hospitals and finance
    firms have been compromised. The flaw allows session hijacking without
    credentials. CISA issued an emergency directive to patch immediately.
    """
    result = tag_article(test_title, test_content)
    print("\n--- Groq AI Tagger Output ---")
    print(json.dumps(result, indent=2))