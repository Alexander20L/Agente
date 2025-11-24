import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')

r = requests.get('https://openrouter.ai/api/v1/models', headers={
    'Authorization': f'Bearer {api_key}'
})

models = r.json()['data']

# Filtrar modelos gratuitos
free_models = [m for m in models if ':free' in m['id']]

print("Modelos GRATUITOS disponibles en OpenRouter:")
print("="*60)
for m in free_models[:15]:
    print(f"  - {m['id']}")
    print(f"    Nombre: {m['name']}")
    print()
