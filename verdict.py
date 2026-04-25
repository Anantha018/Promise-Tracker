import json
import re
from datetime import datetime
from groq import Groq
from database import get_conn

GROQ_API_KEY = "YOUR_API_KEY"
MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=GROQ_API_KEY)

POLITICIAN_CONTEXT = {
    "trump": "US President Donald Trump's 2024 campaign promises.",
    "wes_moore": "Maryland Governor Wes Moore's campaign promises for the state of Maryland.",
    "modi": "Indian Prime Minister Narendra Modi's BJP manifesto promises for India.",
}

def analyze_promise(text: str, politician: str, articles: list) -> dict:
    context = POLITICIAN_CONTEXT.get(politician, "")
    evidence = "RECENT NEWS:\n" + "\n".join(
        f"- {a['title']} ({a['source']})" for a in articles[:6]
    ) if articles else "Limited evidence — using general knowledge."

    prompt = f"""You are a nonpartisan political fact-checker analyzing: {context}

PROMISE: "{text}"

EVIDENCE:
{evidence}

Return ONLY a JSON object:
{{
  "status": "kept" | "broken" | "in_progress" | "partial" | "reversed" | "unknown",
  "verdict": "2-3 sentence factual explanation of what happened",
  "confidence": "high" | "medium" | "low"
}}

Be factual and nonpartisan. No opinion."""

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=300,
        )
        raw = re.sub(r"```json|```", "", resp.choices[0].message.content.strip()).strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"    Groq error: {e}")
    return {"status": "unknown", "verdict": "Could not analyze.", "confidence": "low"}


def run_verdicts():
    conn = get_conn()
    for politician in ["trump", "wes_moore", "modi"]:
        print(f"\n🧠 Analyzing {politician}...")
        promises = conn.execute(
            "SELECT id, text FROM promises WHERE politician=?", (politician,)
        ).fetchall()

        for promise in promises:
            pid, text = promise["id"], promise["text"]
            articles = conn.execute(
                "SELECT title, source FROM news_articles WHERE promise_id=?", (pid,)
            ).fetchall()

            result = analyze_promise(text, politician, articles)
            conn.execute(
                "UPDATE promises SET status=?, verdict=?, last_updated=? WHERE id=?",
                (result["status"], result["verdict"], datetime.now().isoformat(), pid)
            )
            conn.commit()

            emoji = {"kept":"✅","broken":"❌","in_progress":"🔄","partial":"⚠️","reversed":"🔁"}.get(result["status"],"❓")
            print(f"    {emoji} {text[:55]}...")

    conn.close()
    print("\n✅ All verdicts done")

if __name__ == "__main__":
    run_verdicts()