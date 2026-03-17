import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict

from app.core.config import settings
from app.ai.tools.risk_databases import FMEA_Lookup
from app.ai.agents.validators import ValidationResult

class RiskItem(BaseModel):
    risk_category: str = Field(description="Category of the risk (e.g., Mechanical, Electrical, Thermal, Manufacturing, Integration).")
    cause: str = Field(description="A clear engineering cause for the risk based on physical hardware.")
    trade_off: str = Field(description="A key engineering trade-off associated with the risk.")

class RiskChecklist(BaseModel):
    risks: List[RiskItem] = Field(description="List of engineering risks and trade-offs.")

# Generator
generator_llm = ChatGroq(temperature=0.7, model_name="llama-3.3-70b-versatile", groq_api_key=settings.GROQ_API_KEY)
generator_with_tools = generator_llm.bind_tools([FMEA_Lookup])

generator_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Risk Analyst. Identify early engineering risks and trade-offs based on the physical solution mechanisms selected. Rules:\n1) Focus strictly on Mechanical, Electrical, Thermal, Manufacturing, and Integration domains.\n2) Reject generic business/market risks.\n3) Clearly identify an engineering cause and the related design trade-off.\n4) Generate AT LEAST ONE specific valid risk.\nYou can use FMEA_Lookup tool to get standard risk categories."),
    ("human", "Problem Statement: {problem_statement}\nMorphological Chart (Selected Options): {morphological_alternatives}\n\nValidation Feedback (if any): {validation_feedback}\n\nPlease generate the risk checklist.")
])

phase3_generator = generator_prompt | generator_with_tools.with_structured_output(RiskChecklist)

# Validator
validator_llm = ChatGroq(temperature=0.0, model_name="llama-3.1-8b-instant", groq_api_key=settings.GROQ_API_KEY)

validator_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an Engineering Validator. Evaluate the structured engineering risk checklist. Rules to check:\n1) No generic business or market risks (must be engineering specific).\n2) Must have a clear engineering cause.\n3) Must clearly identify a trade-off.\n4) The risk checklist MUST contain at least one valid risk.\nIf valid, return is_valid=True and empty feedback. If invalid, return is_valid=False and detail the exact violations."),
    ("human", "Risk Checklist JSON to validate: {risk_checklist}")
])

phase3_validator = validator_prompt | validator_llm.with_structured_output(ValidationResult)
