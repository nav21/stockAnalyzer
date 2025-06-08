import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', "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"))

def get_food_explanation(food_name):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides brief, interesting explanations about foods."},
                {"role": "user", "content": f"Give me a brief, interesting explanation about {food_name}. Keep it under 2 sentences."}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting explanation: {str(e)}" 