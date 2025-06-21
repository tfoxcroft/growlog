import os
import json
import requests
import logging
from typing import Optional

class DeepseekService:
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.deepseek.com/v1"
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("Deepseek API key not provided and DEEPSEEK_API_KEY environment variable not set")

    def generate_care_guidelines(self, plant_type: str) -> str:
        """Generate plant care guidelines using Deepseek API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Generate simple care guidelines for a {plant_type} plant.
            Return ONLY a single paragraph with basic care instructions.
            
            Example: "Water chives when the soil is dry to the touch..."
            
            Do not include markdown, JSON, or any formatting. Return only the plain text care guidelines.
            """
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Deepseek API request failed: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error processing Deepseek API response: {str(e)}")
            raise