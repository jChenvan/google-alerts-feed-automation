import pydantic


"""
- "company_name": The name of the company involved in manufacturing or selling.
- "weapon_system": The specific type of weapon, vehicle, or military equipment.
- "destination_country": The country receiving the goods.
- "sale_value": The monetary value of the deal, including currency (e.g., "$15 Billion CAD").
- "summary": A concise, one-sentence summary of the export deal or report.
"""

class Transaction(pydantic.BaseModel):
    """A Pydantic model to represent a user's profile."""
    company_name: str = pydantic.Field(description="The name of the company involved in manufacturing or selling.")
    weapon_system: str = pydantic.Field(description="The specific type of weapon, vehicle, or military equipment.")
    destination_country: str = pydantic.Field(description="The country receiving the goods.")
    sale_value: str = pydantic.Field(description="The monetary value of the deal, including currency (e.g., $15 Billion CAD).")
    summary: str = pydantic.Field(description="A concise, one-sentence summary of the export deal or report.")