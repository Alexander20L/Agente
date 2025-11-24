"""
Business-Focused C4 Diagram Generator
Combines static analysis with AI to generate business-context diagrams
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from groq import Groq

from . import analyzer
from . import diagram_generator_deterministic as deterministic
from .distributed_detector import DistributedSystemDetector


class BusinessC4Generator:
    """
    Hybrid generator that combines:
    1. Static analysis (technical structure) - Fast, precise
    2. AI agent (business context) - Understands purpose, flow
    
    Result: C4 diagrams with business terminology, not just technical names
    """
    
    def __init__(self):
        self.distributed_detector = DistributedSystemDetector()
        
        # Initialize Groq client for AI analysis
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-70b-versatile"
        
        # System prompt for business analysis
        self.system_prompt = """You are an expert business analyst and software architect.
        
Your job is to extract BUSINESS TERMINOLOGY from code and documentation.

RULES:
1. Use domain-specific terms (not generic "User", "Service", "Component")
2. Names must be SHORT (max 3 words) for diagram clarity
3. Identify business processes (not just technical functions)
4. Extract user roles from documentation
5. Understand data flow in business terms

EXAMPLES:
- Technical: "user.py" → Business: "Cliente"
- Technical: "process_payment()" → Business: "Procesa Transacción"
- Technical: "validator.py" → Business: "Validador de Crédito"
- Technical: "genetic_algorithm.py" → Business: "Motor Evolutivo"

Respond ONLY in valid JSON format."""
    
    def generate_business_c4(self, project_path: str) -> Dict:
        """
        Main workflow:
        1. Static analysis (structure, technology)
        2. AI extracts business context
        3. Merge both to generate enriched diagrams
        """
        print("🔍 Fase 1: Análisis estático...")
        static_analysis = analyzer.analyze_project(project_path)
        
        print("🏗️ Fase 2: Detección de arquitectura distribuida...")
        arch_info = self.distributed_detector.detect_architecture_type(project_path)
        
        print("🤖 Fase 3: Extracción de contexto de negocio...")
        business_context = self._extract_business_context(project_path, static_analysis, arch_info)
        
        print("🎨 Fase 4: Generación de diagramas enriquecidos...")
        diagrams = self._generate_enriched_diagrams(static_analysis, business_context, arch_info)
        
        return {
            'static_analysis': static_analysis,
            'business_context': business_context,
            'architecture_info': arch_info,
            'diagrams': diagrams
        }
    
    def _extract_business_context(self, project_path: str, static_analysis: Dict, arch_info: Dict) -> Dict:
        """
        Extract business terminology and context using AI
        
        Steps:
        1. Read README (primary source of business context)
        2. Read main entry point (understand flow)
        3. Read key classes with docstrings
        4. Ask AI to extract business vocabulary
        """
        # 1. Read README
        readme_content = self._read_readme(project_path)
        
        # 2. Read main entry point
        main_file = self._find_main_file(project_path, static_analysis)
        main_content = self._read_file(main_file, max_lines=100) if main_file else ""
        
        # 3. Read key classes
        key_classes = self._read_key_classes(project_path, static_analysis)
        
        # 4. Ask AI to extract business vocabulary
        prompt = f"""Analyze this project and extract business terminology.

README:
{readme_content[:2000]}

MAIN CODE:
{main_content[:1500]}

KEY CLASSES:
{json.dumps(key_classes, indent=2)[:2000]}

DETECTED TECHNOLOGIES:
{json.dumps(static_analysis.get('frameworks', []), indent=2)}

ARCHITECTURE TYPE: {arch_info.get('type', 'monolithic')}
{f"SERVICES: {len(arch_info.get('services', []))} microservices detected" if arch_info.get('services') else ""}
{f"CLOUD: {arch_info.get('infrastructure', {}).get('cloud_provider', 'None')}" if arch_info.get('infrastructure') else ""}

Extract and respond in JSON:
{{
    "domain": "Business domain (e.g., Banking, E-commerce, Bioinformatics)",
    "purpose": "What problem does this system solve? (1 sentence)",
    "actors": [
        {{
            "technical": "user",
            "business": "Specific role (e.g., Investigador, Cliente, Cajero)",
            "actions": "What they do (short)"
        }}
    ],
    "processes": [
        {{
            "technical": "run_simulation",
            "business": "Business term (e.g., Ejecuta Experimento)",
            "description": "What it does in business terms"
        }}
    ],
    "components": [
        {{
            "technical": "genetic_algorithm.py",
            "business": "Business name (e.g., Motor Evolutivo)",
            "purpose": "Business purpose (short)"
        }}
    ],
    "entities": [
        {{
            "technical": "Bacteria",
            "business": "Business term (e.g., Población Bacteriana)"
        }}
    ],
    "data_flow": "Describe end-to-end flow in business terms (1 sentence)"
}}

IMPORTANT:
- All "business" names must be MAX 3 words
- Use specific domain terminology
- Extract from README and docstrings
- If unclear, infer from code structure"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            business_context = json.loads(content)
            return business_context
            
        except Exception as e:
            print(f"⚠️ Error extracting business context: {e}")
            # Return minimal context
            return {
                "domain": "Unknown",
                "purpose": "System purpose not detected",
                "actors": [],
                "processes": [],
                "components": [],
                "entities": [],
                "data_flow": "Flow not detected"
            }
    
    def _generate_enriched_diagrams(self, static_analysis: Dict, business_context: Dict, arch_info: Dict) -> Dict:
        """
        Generate C4 diagrams enriched with business context
        
        Strategy:
        - Use static analysis for structure and technology
        - Use business context for names and descriptions
        - Use arch_info for distributed systems
        """
        c1 = self._generate_c1_enriched(static_analysis, business_context)
        
        # Use microservices-specific C2 if detected
        if arch_info.get('type') in ['microservices', 'distributed'] and arch_info.get('services'):
            c2 = self.distributed_detector.generate_c2_for_microservices(arch_info['services'])
        else:
            c2 = self._generate_c2_enriched(static_analysis, business_context)
        
        c3 = self._generate_c3_enriched(static_analysis, business_context)
        
        return {
            'c1': c1,
            'c2': c2,
            'c3': c3
        }
    
    def _generate_c1_enriched(self, static: Dict, business: Dict) -> str:
        """
        C1 - Context diagram with business actors
        
        Enrichments:
        - Actor names from business context (not "Usuario")
        - System name from business purpose
        - External systems with business descriptions
        """
        system_name = self._get_system_name(static, business)
        
        mermaid = "graph TB\n"
        
        # Add actors with business roles
        actors = business.get('actors', [])
        if not actors:
            # Fallback: infer from UI framework
            actors = [{"business": "Usuario", "actions": "Usa el sistema"}]
        
        for i, actor in enumerate(actors):
            actor_id = f"Actor{i}"
            actor_label = actor['business']
            mermaid += f'    {actor_id}["{actor_label}"]\n'
        
        # System node
        system_id = "Sistema"
        system_label = f"{system_name}<br/>{business.get('domain', 'Sistema')}"
        mermaid += f'    {system_id}["{system_label}"]\n'
        
        # Relationships with business actions
        for i, actor in enumerate(actors):
            actor_id = f"Actor{i}"
            action = actor.get('actions', 'Usa')
            mermaid += f'    {actor_id} -->|{action}| {system_id}\n'
        
        # External systems
        external_systems = static.get('external_dependencies', [])
        for i, ext in enumerate(external_systems[:3]):  # Max 3 for clarity
            ext_id = f"Ext{i}"
            ext_name = ext.get('name', 'Sistema Externo')
            mermaid += f'    {ext_id}["{ext_name}"]\n'
            mermaid += f'    {system_id} -->|Integra con| {ext_id}\n'
        
        # Database
        if static.get('database'):
            db = static['database']
            db_name = db.get('type', 'Base de Datos')
            mermaid += f'    DB["{db_name}"]\n'
            mermaid += f'    {system_id} -->|Almacena datos| DB\n'
        
        return mermaid
    
    def _generate_c2_enriched(self, static: Dict, business: Dict) -> str:
        """
        C2 - Container diagram with business names
        
        Enrichments:
        - Container names from business context
        - Technology from static analysis
        - Purpose from business context
        """
        # Get containers from static analysis
        containers = deterministic._detect_containers(static)
        
        mermaid = "graph TB\n"
        
        # Map containers to business names
        component_map = {c['technical']: c['business'] 
                        for c in business.get('components', [])}
        
        for container in containers:
            container_id = container['id']
            
            # Try to get business name
            tech_name = container['name']
            business_name = component_map.get(tech_name, tech_name)
            
            # Format: Business Name [Technology]
            tech = container['technology']
            label = f"{business_name}<br/>[{tech}]"
            
            mermaid += f'    {container_id}["{label}"]\n'
        
        # Add relationships
        if len(containers) >= 2:
            # Simple flow: first container uses second
            mermaid += f'    {containers[0]["id"]} -->|Usa| {containers[1]["id"]}\n'
        
        return mermaid
    
    def _generate_c3_enriched(self, static: Dict, business: Dict) -> str:
        """
        C3 - Component diagram with business names and flow
        
        Enrichments:
        - Component names from business context
        - Business processes as relationships
        - Data flow from business context
        """
        # Get components grouped by layer
        components = static.get('components', [])
        
        # Map to business names
        component_map = {c['technical']: c 
                        for c in business.get('components', [])}
        
        # Group by layer
        layers = {
            'presentation': [],
            'application': [],
            'domain': [],
            'infrastructure': []
        }
        
        for comp in components[:20]:  # Limit for clarity
            layer = comp.get('layer', 'application')
            
            # Get business name
            tech_name = comp['name']
            business_data = component_map.get(tech_name, {})
            business_name = business_data.get('business', tech_name.replace('.py', '').title())
            
            layers[layer].append({
                'id': comp['name'].replace('.', '_').replace('/', '_'),
                'business_name': business_name,
                'technical_name': tech_name
            })
        
        # Generate Mermaid
        mermaid = "graph TB\n"
        
        layer_names = {
            'presentation': 'Presentación',
            'application': 'Aplicación',
            'domain': 'Dominio',
            'infrastructure': 'Infraestructura'
        }
        
        all_components = []
        for layer_key in ['presentation', 'application', 'domain', 'infrastructure']:
            layer_comps = layers[layer_key]
            if not layer_comps:
                continue
            
            layer_name = layer_names[layer_key]
            mermaid += f'    subgraph {layer_name}\n'
            
            for comp in layer_comps:
                comp_id = comp['id']
                label = comp['business_name']
                mermaid += f'        {comp_id}["{label}"]\n'
                all_components.append(comp)
            
            mermaid += '    end\n'
        
        # Add relationships with business process names
        processes = business.get('processes', [])
        process_map = {p['technical']: p['business'] for p in processes}
        
        # Simple flow based on layers
        if len(all_components) >= 2:
            # Connect presentation → application → domain
            for i in range(min(3, len(all_components) - 1)):
                from_comp = all_components[i]
                to_comp = all_components[i + 1]
                
                # Try to find business verb
                verb = process_map.get(to_comp['technical_name'], 'Usa')
                
                mermaid += f'    {from_comp["id"]} -->|{verb}| {to_comp["id"]}\n'
        
        return mermaid
    
    # Helper methods
    
    def _read_readme(self, project_path: str) -> str:
        """Read README file"""
        readme_paths = ['README.md', 'README.txt', 'README.rst', 'readme.md']
        
        for readme_name in readme_paths:
            readme_path = os.path.join(project_path, readme_name)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except:
                    continue
        
        return "No README found"
    
    def _find_main_file(self, project_path: str, static: Dict) -> Optional[str]:
        """Find main entry point"""
        common_names = ['main.py', 'app.py', '__main__.py', 'run.py', 'server.py']
        
        for name in common_names:
            path = os.path.join(project_path, name)
            if os.path.exists(path):
                return path
        
        # Fallback: first .py file with main function
        structure = static.get('structure', {})
        for file_path, file_info in structure.items():
            if 'main' in file_info.get('functions', []):
                return os.path.join(project_path, file_path)
        
        return None
    
    def _read_file(self, file_path: str, max_lines: int = 100) -> str:
        """Read file with line limit"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:max_lines]
                return ''.join(lines)
        except:
            return ""
    
    def _read_key_classes(self, project_path: str, static: Dict) -> List[Dict]:
        """Read docstrings from key classes"""
        structure = static.get('structure', {})
        key_classes = []
        
        for file_path, file_info in list(structure.items())[:10]:  # Top 10 files
            for class_name in file_info.get('classes', [])[:2]:  # Top 2 classes per file
                key_classes.append({
                    'file': file_path,
                    'class': class_name,
                    'docstring': file_info.get('docstring', '')[:200]
                })
        
        return key_classes
    
    def _get_system_name(self, static: Dict, business: Dict) -> str:
        """Get system name from business context or project name"""
        purpose = business.get('purpose', '')
        if purpose and purpose != "System purpose not detected":
            # Extract first meaningful phrase
            return purpose.split('.')[0][:50]
        
        # Fallback: project directory name
        return static.get('project_name', 'Sistema')
