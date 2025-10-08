import pytest
from ..scoring import calculate_rule_score
from ..models import Offer, Lead

@pytest.fixture
def sample_offer():
    return Offer(name="Test", value_props=["a"], ideal_use_cases=["B2B SaaS mid-market"])

def test_rule_score_high(sample_offer):
    lead = Lead(name="A", role="Head of Growth", company="C", industry="B2B SaaS mid-market", location="L", linkedin_bio="B")
    assert calculate_rule_score(lead, sample_offer) == 50

def test_rule_score_medium(sample_offer):
    lead = Lead(name="A", role="Manager", company="C", industry="SaaS", location="", linkedin_bio="B")
    assert calculate_rule_score(lead, sample_offer) == 20

def test_rule_score_low(sample_offer):
    lead = Lead(name="A", role="Intern", company="C", industry="Retail", location="L", linkedin_bio="")
    assert calculate_rule_score(lead, sample_offer) == 0