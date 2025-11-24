"""
Microservices and Distributed Systems Detector
Extends BusinessC4Generator for complex architectures
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional


class DistributedSystemDetector:
    """
    Detects microservices, cloud services, and distributed patterns
    
    Handles:
    - Microservices (multiple services in one repo)
    - Docker/Kubernetes deployments
    - Cloud services (AWS, Azure, GCP)
    - Message queues (RabbitMQ, Kafka)
    - Service mesh (Istio, Linkerd)
    """
    
    def __init__(self):
        self.microservice_indicators = [
            'docker-compose.yml',
            'docker-compose.yaml',
            'kubernetes/',
            'k8s/',
            'helm/',
            'services/',
            'microservices/',
        ]
        
        self.cloud_indicators = {
            'aws': ['serverless.yml', 'sam.yaml', 'cloudformation/', 'lambda/', 'cdk/'],
            'azure': ['azure-pipelines.yml', 'arm-templates/', 'function.json'],
            'gcp': ['app.yaml', 'cloudbuild.yaml', 'functions/'],
        }
    
    def detect_architecture_type(self, project_path: str) -> Dict:
        """
        Detect if project is monolithic, microservices, or serverless
        
        Returns:
        {
            'type': 'monolithic' | 'microservices' | 'serverless' | 'distributed',
            'indicators': [...],
            'services': [...],
            'infrastructure': {...}
        }
        """
        result = {
            'type': 'monolithic',
            'indicators': [],
            'services': [],
            'infrastructure': {}
        }
        
        # Check for microservices
        if self._has_microservices(project_path):
            result['type'] = 'microservices'
            result['services'] = self._detect_microservices(project_path)
            result['indicators'].append('Multiple services detected')
        
        # Check for serverless
        cloud_type = self._detect_cloud_provider(project_path)
        if cloud_type:
            if result['type'] == 'microservices':
                result['type'] = 'distributed'
            else:
                result['type'] = 'serverless'
            result['infrastructure']['cloud_provider'] = cloud_type
            result['indicators'].append(f'Cloud deployment: {cloud_type}')
        
        # Check for container orchestration
        orchestration = self._detect_orchestration(project_path)
        if orchestration:
            result['infrastructure']['orchestration'] = orchestration
            result['indicators'].append(f'Container orchestration: {orchestration}')
        
        # Check for message queues
        message_queue = self._detect_message_queue(project_path)
        if message_queue:
            result['infrastructure']['message_queue'] = message_queue
            result['indicators'].append(f'Message queue: {message_queue}')
        
        return result
    
    def _has_microservices(self, project_path: str) -> bool:
        """Check if project has microservices structure"""
        for indicator in self.microservice_indicators:
            path = os.path.join(project_path, indicator)
            if os.path.exists(path):
                return True
        
        # Check for multiple services in subdirectories
        services_dir = os.path.join(project_path, 'services')
        if os.path.exists(services_dir) and os.path.isdir(services_dir):
            subdirs = [d for d in os.listdir(services_dir) 
                      if os.path.isdir(os.path.join(services_dir, d))]
            if len(subdirs) >= 2:
                return True
        
        return False
    
    def _detect_microservices(self, project_path: str) -> List[Dict]:
        """
        Detect individual microservices in the project
        
        Returns list of:
        {
            'name': 'user-service',
            'path': 'services/user',
            'type': 'REST API',
            'port': 8001,
            'dependencies': ['database', 'cache']
        }
        """
        services = []
        
        # Check services/ directory
        services_dir = os.path.join(project_path, 'services')
        if os.path.exists(services_dir):
            for service_name in os.listdir(services_dir):
                service_path = os.path.join(services_dir, service_name)
                if os.path.isdir(service_path):
                    service_info = self._analyze_service(service_name, service_path)
                    services.append(service_info)
        
        # Check docker-compose.yml
        docker_compose = os.path.join(project_path, 'docker-compose.yml')
        if os.path.exists(docker_compose):
            compose_services = self._parse_docker_compose(docker_compose)
            services.extend(compose_services)
        
        return services
    
    def _analyze_service(self, name: str, path: str) -> Dict:
        """Analyze individual service"""
        service = {
            'name': name,
            'path': path,
            'type': 'Service',
            'port': None,
            'dependencies': []
        }
        
        # Detect service type
        if os.path.exists(os.path.join(path, 'api')):
            service['type'] = 'REST API'
        elif os.path.exists(os.path.join(path, 'consumer')):
            service['type'] = 'Message Consumer'
        elif os.path.exists(os.path.join(path, 'worker')):
            service['type'] = 'Background Worker'
        
        # Check for config files to find port
        env_file = os.path.join(path, '.env')
        if os.path.exists(env_file):
            port = self._extract_port_from_env(env_file)
            if port:
                service['port'] = port
        
        # Check dependencies
        requirements = os.path.join(path, 'requirements.txt')
        if os.path.exists(requirements):
            deps = self._extract_dependencies(requirements)
            service['dependencies'] = deps
        
        return service
    
    def _parse_docker_compose(self, compose_file: str) -> List[Dict]:
        """Parse docker-compose.yml to extract services"""
        services = []
        
        try:
            import yaml
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            if 'services' in compose_data:
                for service_name, service_config in compose_data['services'].items():
                    service = {
                        'name': service_name,
                        'path': service_config.get('build', {}).get('context', './'),
                        'type': 'Container',
                        'port': None,
                        'dependencies': service_config.get('depends_on', [])
                    }
                    
                    # Extract port
                    ports = service_config.get('ports', [])
                    if ports:
                        port_mapping = str(ports[0])
                        if ':' in port_mapping:
                            service['port'] = int(port_mapping.split(':')[0])
                    
                    # Detect type from image
                    image = service_config.get('image', '')
                    if 'postgres' in image or 'mysql' in image:
                        service['type'] = 'Database'
                    elif 'redis' in image:
                        service['type'] = 'Cache'
                    elif 'rabbitmq' in image or 'kafka' in image:
                        service['type'] = 'Message Queue'
                    elif 'nginx' in image:
                        service['type'] = 'Web Server'
                    
                    services.append(service)
        
        except Exception as e:
            print(f"Error parsing docker-compose.yml: {e}")
        
        return services
    
    def _detect_cloud_provider(self, project_path: str) -> Optional[str]:
        """Detect cloud provider (AWS, Azure, GCP)"""
        for provider, indicators in self.cloud_indicators.items():
            for indicator in indicators:
                path = os.path.join(project_path, indicator)
                if os.path.exists(path):
                    return provider.upper()
        return None
    
    def _detect_orchestration(self, project_path: str) -> Optional[str]:
        """Detect container orchestration (Kubernetes, Docker Swarm)"""
        if os.path.exists(os.path.join(project_path, 'kubernetes')) or \
           os.path.exists(os.path.join(project_path, 'k8s')):
            return 'Kubernetes'
        
        if os.path.exists(os.path.join(project_path, 'docker-compose.yml')):
            return 'Docker Compose'
        
        if os.path.exists(os.path.join(project_path, 'helm')):
            return 'Helm (Kubernetes)'
        
        return None
    
    def _detect_message_queue(self, project_path: str) -> Optional[str]:
        """Detect message queue technology"""
        # Check docker-compose
        docker_compose = os.path.join(project_path, 'docker-compose.yml')
        if os.path.exists(docker_compose):
            try:
                with open(docker_compose, 'r') as f:
                    content = f.read().lower()
                    if 'rabbitmq' in content:
                        return 'RabbitMQ'
                    if 'kafka' in content:
                        return 'Apache Kafka'
                    if 'redis' in content and 'pub/sub' in content:
                        return 'Redis Pub/Sub'
            except:
                pass
        
        # Check requirements.txt
        requirements = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(requirements):
            try:
                with open(requirements, 'r') as f:
                    content = f.read().lower()
                    if 'pika' in content or 'rabbitmq' in content:
                        return 'RabbitMQ'
                    if 'kafka-python' in content:
                        return 'Apache Kafka'
                    if 'celery' in content:
                        return 'Celery (with Redis/RabbitMQ)'
            except:
                pass
        
        return None
    
    def _extract_port_from_env(self, env_file: str) -> Optional[int]:
        """Extract port from .env file"""
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('PORT='):
                        return int(line.split('=')[1].strip())
        except:
            pass
        return None
    
    def _extract_dependencies(self, requirements_file: str) -> List[str]:
        """Extract key dependencies"""
        deps = []
        
        key_deps = {
            'psycopg2': 'PostgreSQL',
            'pymongo': 'MongoDB',
            'redis': 'Redis',
            'sqlalchemy': 'Database (SQLAlchemy)',
            'flask': 'Flask',
            'django': 'Django',
            'fastapi': 'FastAPI',
        }
        
        try:
            with open(requirements_file, 'r') as f:
                content = f.read().lower()
                for dep_name, dep_label in key_deps.items():
                    if dep_name in content:
                        deps.append(dep_label)
        except:
            pass
        
        return deps
    
    def generate_c2_for_microservices(self, services: List[Dict]) -> str:
        """
        Generate C2 diagram for microservices architecture
        
        Shows:
        - Each microservice as a container
        - Inter-service communication
        - Shared infrastructure (DB, cache, MQ)
        """
        mermaid = "graph TB\n"
        
        # Group services by type
        api_services = [s for s in services if 'API' in s['type']]
        worker_services = [s for s in services if 'Worker' in s['type'] or 'Consumer' in s['type']]
        infrastructure = [s for s in services if s['type'] in ['Database', 'Cache', 'Message Queue']]
        
        # API Gateway (if multiple APIs)
        if len(api_services) > 1:
            mermaid += '    Gateway["API Gateway<br/>[Kong/Nginx]"]\n'
        
        # API Services
        if api_services:
            mermaid += '    subgraph "API Services"\n'
            for service in api_services:
                service_id = service['name'].replace('-', '_').replace(' ', '_')
                port_info = f":{service['port']}" if service['port'] else ""
                mermaid += f'        {service_id}["{service["name"]}<br/>[{service["type"]}]{port_info}"]\n'
            mermaid += '    end\n'
        
        # Worker Services
        if worker_services:
            mermaid += '    subgraph "Background Processing"\n'
            for service in worker_services:
                service_id = service['name'].replace('-', '_').replace(' ', '_')
                mermaid += f'        {service_id}["{service["name"]}<br/>[{service["type"]}]"]\n'
            mermaid += '    end\n'
        
        # Infrastructure
        for infra in infrastructure:
            infra_id = infra['name'].replace('-', '_').replace(' ', '_')
            mermaid += f'    {infra_id}["{infra["name"]}<br/>[{infra["type"]}]"]\n'
        
        # Relationships
        if len(api_services) > 1:
            for service in api_services:
                service_id = service['name'].replace('-', '_').replace(' ', '_')
                mermaid += f'    Gateway -->|Routes| {service_id}\n'
        
        # Connect services to infrastructure
        for service in api_services + worker_services:
            service_id = service['name'].replace('-', '_').replace(' ', '_')
            
            for dep in service.get('dependencies', []):
                # Find matching infrastructure
                for infra in infrastructure:
                    if dep.lower() in infra['name'].lower():
                        infra_id = infra['name'].replace('-', '_').replace(' ', '_')
                        mermaid += f'    {service_id} -->|Uses| {infra_id}\n'
        
        return mermaid


def enhance_business_c4_with_distributed(business_c4_generator, project_path: str) -> Dict:
    """
    Enhance BusinessC4Generator with distributed system detection
    
    Usage:
    >>> from core.business_c4_generator import BusinessC4Generator
    >>> gen = BusinessC4Generator()
    >>> result = enhance_business_c4_with_distributed(gen, project_path)
    """
    detector = DistributedSystemDetector()
    
    # Detect architecture type
    arch_info = detector.detect_architecture_type(project_path)
    
    # Standard business C4 analysis
    result = business_c4_generator.generate_business_c4(project_path)
    
    # Enhance with distributed info
    result['architecture_type'] = arch_info['type']
    result['distributed_info'] = arch_info
    
    # If microservices, regenerate C2 with service-oriented view
    if arch_info['type'] in ['microservices', 'distributed']:
        services = arch_info.get('services', [])
        if services:
            microservices_c2 = detector.generate_c2_for_microservices(services)
            result['diagrams']['c2_microservices'] = microservices_c2
            
            # Add metadata
            result['business_context']['architecture_style'] = arch_info['type']
            result['business_context']['services_count'] = len(services)
    
    return result
