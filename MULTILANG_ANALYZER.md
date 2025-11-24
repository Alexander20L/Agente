# 🌍 Analyzer Multi-Lenguaje - Documentación Completa

## 📋 Resumen

El **analyzer.py** del AGENTE ahora soporta análisis de arquitectura para **CUALQUIER proyecto** moderno, no solo Python. Se han implementado detectores universales para 11+ lenguajes de programación.

---

## 🎯 Lenguajes Soportados

| Lenguaje | Ecosistema | Frameworks Detectados |
|----------|------------|----------------------|
| **Python** | pip, conda | FastAPI, Flask, Django, PyQt5, Streamlit |
| **JavaScript/TypeScript** | npm, yarn | Express, NestJS, React, Vue, Angular |
| **Java** | Maven, Gradle | Spring Boot, Spring MVC, Hibernate |
| **C#** | NuGet, .csproj | ASP.NET Core, Entity Framework, WPF |
| **Go** | go.mod | Gin, Echo, http stdlib |
| **Rust** | Cargo | actix-web, rocket, warp, axum |
| **PHP** | Composer | Laravel, Symfony |
| **Ruby** | Bundler, Gem | Rails, Sinatra |
| **Kotlin** | Gradle, Maven | Ktor, Spring Boot |
| **Swift** | SPM, CocoaPods | SwiftUI, UIKit |
| **Dart** | pub | Flutter |

---

## 🔍 Tipos de Proyecto Detectados

```python
TIPOS = [
    "library",          # Biblioteca/SDK
    "compiler",         # Compilador, DSL, JIT
    "api-backend",      # REST API, GraphQL
    "gui-application",  # Desktop GUI (Qt, WPF, Electron)
    "ml-app",           # Machine Learning
    "mobile-app",       # iOS, Android, React Native, Flutter
    "microservice",     # Arquitectura de microservicios
    "unknown"           # No clasificado
]
```

---

## 📦 Funciones Principales

### 1. `detect_project_type(analysis_result)`

Detecta el tipo de proyecto analizando:

**Java/Spring Boot:**
```java
// Detecta pom.xml, build.gradle
@SpringBootApplication  // → api-backend
@RestController
@Controller
```

**C#/ASP.NET Core:**
```csharp
// Detecta .csproj, Program.cs
[ApiController]  // → api-backend
[Route("api/[controller]")]
```

**Go:**
```go
// Detecta go.mod, main.go
http.ListenAndServe()  // → api-backend
gin.Default()
echo.New()
```

**Rust:**
```rust
// Detecta Cargo.toml
[dependencies]
actix-web = "*"  // → api-backend
rocket = "*"
```

**PHP/Laravel:**
```php
// Detecta composer.json, artisan
Route::get()  // → api-backend
class UserController extends Controller
```

**Ruby/Rails:**
```ruby
# Detecta Gemfile, config.ru
class UsersController < ApplicationController  # → api-backend
has_many :posts
```

---

### 2. `detect_containers_and_infra(root_path)`

Identifica contenedores C2 (14 secciones):

| Sección | Detecta | Tecnologías |
|---------|---------|-------------|
| #1 | Frontend Web | React, Vue, Angular, Svelte |
| #2 | Frontend UI | Qt, Tkinter, PyQt5, wxPython |
| #3 | API Backend (Python) | FastAPI, Flask, Django |
| #4 | API Backend (Node.js) | Express, NestJS, Koa, Hapi |
| #5 | Database | PostgreSQL, MySQL, MongoDB, Redis |
| #6 | Message Queue | RabbitMQ, Kafka, Redis Pub/Sub |
| #7 | Cache | Redis, Memcached |
| #8 | Filesystem/Storage | AWS S3, MinIO, local storage |
| **#9** | **Java Backend** | **Spring Boot, Spring MVC** |
| **#10** | **C# Backend** | **ASP.NET Core, Web API** |
| **#11** | **Go Backend** | **Gin, Echo, stdlib** |
| **#12** | **Rust Backend** | **actix-web, rocket, warp** |
| **#13** | **PHP Backend** | **Laravel, Symfony** |
| **#14** | **Ruby Backend** | **Rails, Sinatra** |

---

### 3. `detect_components(root_path)`

Detecta componentes C3 analizando:

**Extensiones de archivo soportadas:**
```python
valid_ext = [
    ".py", ".java", ".js", ".ts", ".cs", ".go", 
    ".rs", ".php", ".rb", ".kt", ".swift"
]
```

**Patrones de nomenclatura:**
```python
name_patterns = [
    "controller", "service", "repository", "model", 
    "view", "handler", "endpoint", "api", 
    "usecase", "interactor", "dto", "domain",
    "activity", "fragment"  # Android
]
```

**Detección por contenido (regex multi-lenguaje):**

| Lenguaje | Controller | Service | Repository | Model |
|----------|-----------|---------|------------|-------|
| Java | `@Controller` | `@Service` | `@Repository` | `@Entity` |
| C# | `[ApiController]` | `[Service]` | `[Repository]` | `[Table]` |
| Go | `http.HandleFunc` | `type.*Service` | - | `type.*{` |
| Rust | `#[get]` | `impl.*Service` | - | `struct.*json` |
| PHP | `class.*Controller` | - | - | `class.*Model` |
| Ruby | `class.*Controller` | - | - | `belongs_to` |

---

### 4. Detección de Imports (Multi-lenguaje)

**Python:**
```python
from mymodule import MyClass
import package.submodule
```

**Java:**
```java
import com.example.service.UserService;
```

**C#:**
```csharp
using MyApp.Services;
```

**Go:**
```go
import "github.com/gin-gonic/gin"
```

**Rust:**
```rust
use actix_web::{web, App, HttpServer};
```

**PHP:**
```php
use App\Services\UserService;
```

**Ruby:**
```ruby
require 'rails'
```

**JavaScript/TypeScript:**
```javascript
import express from 'express';
```

---

### 5. Detección de Herencia/Composición

**Python:**
```python
class Dog(Animal):  # → inheritance
```

**Java:**
```java
class Dog extends Animal implements Runnable {
    // → inheritance + implementation
}
```

**C#:**
```csharp
class Dog : Animal, IRunnable {
    // → inheritance + implementation
}
```

**Go:**
```go
type Dog struct {
    Animal  // embedded struct → composition
}
```

**Rust:**
```rust
impl Runnable for Dog {  // → trait implementation
}
```

**PHP:**
```php
class Dog extends Animal implements Runnable {
    // → inheritance + implementation
}
```

**Ruby:**
```ruby
class Dog < Animal  # → inheritance
end
```

**JavaScript/TypeScript:**
```javascript
class Dog extends Animal {  // → inheritance
}
```

---

## 🧪 Testing

### Proyectos de prueba recomendados:

1. **Java Spring Boot:**
   ```bash
   git clone https://github.com/spring-projects/spring-petclinic
   ```

2. **C# ASP.NET Core:**
   ```bash
   git clone https://github.com/dotnet/eShopOnWeb
   ```

3. **Go Gin:**
   ```bash
   git clone https://github.com/gin-gonic/examples
   ```

4. **Rust Actix:**
   ```bash
   git clone https://github.com/actix/examples
   ```

5. **PHP Laravel:**
   ```bash
   git clone https://github.com/laravel/laravel
   ```

6. **Ruby on Rails:**
   ```bash
   git clone https://github.com/rails/rails
   ```

---

## 🚀 Uso con el AGENTE

### Vía API:

```bash
# POST /analyze/advanced
curl -X POST http://localhost:8000/analyze/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "project_path": "path/to/java-spring-project.zip",
    "diagram_level": "C3"
  }'
```

### Vía Python directo:

```python
from core.analyzer import analyze_project

result = analyze_project("path/to/project.zip")

print(f"Project Type: {result['project_type']}")
print(f"Containers: {len(result['containers'])}")
print(f"Components: {len(result['components'])}")
```

---

## 📊 Estadísticas

| Métrica | Valor |
|---------|-------|
| **Líneas de código** | ~1,170 |
| **Lenguajes soportados** | 11+ |
| **Frameworks detectados** | 30+ |
| **Patrones de componentes** | 50+ |
| **Tipos de relación** | 4 (import, inheritance, implementation, composition) |

---

## ✅ Checklist de Implementación

- [x] Detección de tipo de proyecto multi-lenguaje
- [x] Contenedores C2 para Java, C#, Go, Rust, PHP, Ruby
- [x] Componentes C3 con regex multi-lenguaje
- [x] Imports universales (8 lenguajes)
- [x] Herencia y composición (8 lenguajes)
- [x] Clases y entry points (8 lenguajes)
- [ ] Testing con proyectos reales (Java, C#, Go)
- [ ] Generación de C4 diagrams multi-lenguaje
- [ ] Documentación de ejemplos por lenguaje

---

## 🎓 Conceptos Académicos

### Arquitectura Hexagonal (Ports & Adapters)

El analyzer detecta capas arquitectónicas:

```
Controllers  →  Services  →  Repositories  →  Database
(Adapters)     (Use Cases)   (Ports)          (External)
```

### Clean Architecture

Detecta componentes según capas:

```
UI Layer       → Controllers, Views
Application    → Services, Use Cases
Domain         → Entities, Models
Infrastructure → Repositories, Database
```

### DDD (Domain-Driven Design)

Identifica patrones DDD:

- **Entities**: Clases con `@Entity`, `[Table]`
- **Repositories**: Clases con `@Repository`, `interface.*Repository`
- **Services**: Clases con `@Service`, `*Service`
- **DTOs**: Clases con `DTO`, `Request`, `Response`

---

## 🔮 Próximas Mejoras

1. **Análisis de métricas:** Complejidad ciclomática, cobertura
2. **Detección de anti-patrones:** God classes, spaghetti code
3. **Análisis de seguridad:** SQL injection, XSS vulnerabilities
4. **Performance profiling:** Hot paths, bottlenecks
5. **Dependency analysis:** Versiones obsoletas, conflictos

---

## 📝 Notas

- El analyzer funciona con archivos `.zip` (sube proyectos vía API)
- Para proyectos locales, usa directamente `analyze_project(path)`
- La detección es heurística: usa patrones, no compilación completa
- Requiere archivos de texto legibles (no binarios)

---

## 📞 Soporte

Para reportar bugs o sugerir mejoras:
1. Añadir issue en el repositorio
2. Incluir tipo de proyecto y lenguaje
3. Adjuntar logs de `analyzer.py`

---

**Última actualización:** 2025-01-XX  
**Versión:** 2.0 (Multi-lenguaje Universal)
