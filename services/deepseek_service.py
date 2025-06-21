import os
import requests
import logging
from typing import Optional

class DeepseekService:
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.deepseek.com/v1"
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("Deepseek API key not provided and DEEPSEEK_API_KEY environment variable not set")

    def generate_plant_description(self, plant_type: str) -> dict:
        """Generate plant description and care guidelines using Deepseek API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""Generate a detailed description and simple care guidelines for a {plant_type} plant.
            Return ONLY a JSON object with these two fields:
            - "description": A single paragraph describing the plant's characteristics
            - "care_guidelines": A single paragraph with basic care instructions
            
            Example:
            {{
              "description": "Chives are...",
              "care_guidelines": "Water chives..."
            }}
            
            Do not include markdown, nested structures, or additional fields. Dont wrap the response in markdown, return only the json text.
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
                "max_tokens": 1000
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            print(content)
            
            # Parse and simplify the response
            try:
                import json
                response_data = json.loads(content)
                
                # Flatten any nested structures
                description = response_data.get('description', '')
                if isinstance(description, dict):
                    description = ' '.join(str(v) for v in description.values())
                
                care_guidelines = response_data.get('care_guidelines', '')
                if isinstance(care_guidelines, dict):
                    care_guidelines = ' '.join(str(v) for v in care_guidelines.values())
                
                return {
                    'description': description or f"Description for {plant_type}",
                    'care_guidelines': care_guidelines or f"Care guidelines for {plant_type}"
                }
            except:
                return {
                    'description': f"Description for {plant_type}",
                    'care_guidelines': f"Care guidelines for {plant_type}"
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Deepseek API request failed: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error processing Deepseek API response: {str(e)}")
            raise