import os
import json
from dotenv import load_dotenv
import pydantic
from google import genai
from typing import Type, TypeVar

# --- Configuration ---
# To run this, you must have your Google API key set as an environment variable.
# For example:
# export GOOGLE_API_KEY="YOUR_API_KEY"
# The new google-genai library automatically looks for this environment variable.

load_dotenv()

try:
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
except ValueError as e:
    print(f"Error: {e}")


# Define a generic type variable for Pydantic models
PydanticModel = TypeVar("PydanticModel", bound=pydantic.BaseModel)

# --- Pydantic Schemas for Demonstration ---

class UserProfile(pydantic.BaseModel):
    """A Pydantic model to represent a user's profile."""
    name: str = pydantic.Field(description="The full name of the user.")
    age: int = pydantic.Field(description="The age of the user.")
    email: pydantic.EmailStr = pydantic.Field(description="The user's email address.")
    is_active: bool = pydantic.Field(description="Indicates if the user account is active.")

class Meeting(pydantic.BaseModel):
    """A Pydantic model for meeting details."""
    topic: str = pydantic.Field(description="The main subject of the meeting.")
    attendees: list[str] = pydantic.Field(description="A list of names of the people attending.")
    duration_minutes: int = pydantic.Field(description="The scheduled duration of the meeting in minutes.")


# --- Core Function ---

def get_object_from_string(
    text_input: str,
    schema: Type[PydanticModel],
    extra_prompts: str|None = None,
) -> PydanticModel | None:
    """
    Extracts information from a text string into a Pydantic object using the latest google-genai SDK.

    Args:
        text_input: The unstructured text string to process.
        schema: The Pydantic model class to use for structuring the output.
        prompts: Any additional prompting on top of the default prompts. Optional.

    Returns:
        An instance of the provided Pydantic schema populated with extracted data,
        or None if the operation fails.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        print("API key is not configured. Cannot proceed with extraction.")
        return None

    try:
        # Initialize the client. It automatically uses the GOOGLE_API_KEY env var.
        client = genai.Client()

        # The prompt instructs the model on its task and provides the text.
        prompt = f"""
        Analyze the following text and extract the information into a JSON object
        that strictly follows the provided schema.

        {extra_prompts}

        Text to analyze:
        ---
        {text_input}
        ---
        """

        # Use the client to generate content with the specified model and config
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
            }
        )

        # The response text should be a valid JSON string conforming to the schema.
        # We can now parse it directly using the Pydantic model.
        json_string = response.text
        if (json_string == None):
            return None
        validated_object = schema.model_validate_json(json_string)
        return validated_object

    except Exception as e:
        print(f"An error occurred during extraction or validation: {e}")
        # This can happen if the model fails to generate valid JSON
        # or if there's a network issue.
        return None

# --- Example Usage ---

if __name__ == "__main__":
    print("--- Example 1: Extracting User Profile ---")
    user_text = """
    John Doe is 34 years old and his contact email is john.doe@example.com.
    His account is currently enabled and in good standing.
    """
    user_profile_obj = get_object_from_string(user_text, UserProfile)

    if user_profile_obj:
        print(f"Successfully extracted object: {type(user_profile_obj)}")
        print(user_profile_obj.model_dump_json(indent=2))
        print(f"User's name: {user_profile_obj.name}")
        print(f"User's email: {user_profile_obj.email}")
    else:
        print("Failed to extract user profile.")

    print("\n" + "="*40 + "\n")

    print("--- Example 2: Extracting Meeting Details ---")
    meeting_text = """
    Let's schedule a project kickoff meeting for tomorrow.
    We need to invite Alice, Bob, and Charlie. The meeting should last for 45 minutes.
    """
    meeting_obj = get_object_from_string(meeting_text, Meeting)

    if meeting_obj:
        print(f"Successfully extracted object: {type(meeting_obj)}")
        print(meeting_obj.model_dump_json(indent=2))
        print(f"Meeting Topic: {meeting_obj.topic}")
        print(f"Attendees: {', '.join(meeting_obj.attendees)}")
    else:
        print("Failed to extract meeting details.")
