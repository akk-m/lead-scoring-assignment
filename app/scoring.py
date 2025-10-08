import google.generativeai as genai
from .models import Offer, Lead, ScoredLead
from typing import List
import os

offer_storage: Offer = None
leads_storage: List[Lead] = []
results_storage: List[ScoredLead] = []

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def calculate_rule_score(lead: Lead, offer: Offer) -> int:
    score = 0
    role_lower = lead.role.lower()
    if any(kw in role_lower for kw in ["head", "director", "vp", "ceo", "cto", "cmo", "cfo"]):
        score += 20
    elif any(kw in role_lower for kw in ["manager", "specialist", "lead"]):
        score += 10
    industry_lower = lead.industry.lower()
    if any(case.lower() == industry_lower for case in offer.ideal_use_cases):
        score += 20
    elif any(word in industry_lower for case in offer.ideal_use_cases for word in case.lower().split()):
        score += 10
    if all(getattr(lead, field) for field in lead.dict()):
        score += 10
    return score

async def get_ai_intent(lead: Lead, offer: Offer) -> tuple[str, int, str]:
    prompt = f"""
    Product/Offer: {offer.name}
    Value Props: {', '.join(offer.value_props)}
    Ideal Use Cases: {', '.join(offer.ideal_use_cases)}
    Prospect Details: Name: {lead.name}, Role: {lead.role}, Company: {lead.company}, Industry: {lead.industry}, Location: {lead.location}, LinkedIn Bio: {lead.linkedin_bio}
    Classify intent (High/Medium/Low) and explain in 1-2 sentences.
    Output: Intent: [High/Medium/Low]\nExplanation: [text]
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    content = response.text.strip()
    intent = content.split("\n")[0].split(": ")[1]
    explanation = content.split("\n")[1].split(": ")[1]
    points = {"High": 50, "Medium": 30, "Low": 10}.get(intent, 10)
    return intent, points, explanation

async def score_leads() -> List[ScoredLead]:
    if not offer_storage or not leads_storage:
        raise ValueError("Missing offer or leads")
    results = []
    for lead in leads_storage:
        rule_score = calculate_rule_score(lead, offer_storage)
        intent, ai_points, ai_exp = await get_ai_intent(lead, offer_storage)
        score = rule_score + ai_points
        rule_exp = f"Role: {'decision maker' if rule_score >= 20 else 'influencer' if rule_score >= 10 else 'none'}. Industry: {'exact' if rule_score >= 20 else 'adjacent' if rule_score >= 10 else 'none'}."
        reasoning = f"{rule_exp} {ai_exp}"
        results.append(ScoredLead(name=lead.name, role=lead.role, company=lead.company, intent=intent, score=score, reasoning=reasoning))
    global results_storage
    results_storage = results
    return results