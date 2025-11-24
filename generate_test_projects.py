"""
Generador de proyectos sintéticos para testing multi-lenguaje
Crea estructuras de proyectos mínimas pero realistas
"""
import os
import shutil
import zipfile

def create_go_project():
    """Crea proyecto Go básico (API REST)"""
    base = "test_projects/go_api"
    os.makedirs(base, exist_ok=True)
    
    # go.mod
    with open(f"{base}/go.mod", 'w') as f:
        f.write("""module example.com/api

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    gorm.io/gorm v1.25.5
)
""")
    
    # main.go
    with open(f"{base}/main.go", 'w') as f:
        f.write("""package main

import (
    "github.com/gin-gonic/gin"
    "example.com/api/controllers"
    "example.com/api/models"
)

func main() {
    r := gin.Default()
    r.GET("/users", controllers.GetUsers)
    r.POST("/users", controllers.CreateUser)
    r.Run(":8080")
}
""")
    
    # controllers/user_controller.go
    os.makedirs(f"{base}/controllers", exist_ok=True)
    with open(f"{base}/controllers/user_controller.go", 'w') as f:
        f.write("""package controllers

import (
    "github.com/gin-gonic/gin"
    "example.com/api/services"
)

func GetUsers(c *gin.Context) {
    users := services.GetAllUsers()
    c.JSON(200, users)
}

func CreateUser(c *gin.Context) {
    // Implementation
}
""")
    
    # services/user_service.go
    os.makedirs(f"{base}/services", exist_ok=True)
    with open(f"{base}/services/user_service.go", 'w') as f:
        f.write("""package services

import "example.com/api/models"

func GetAllUsers() []models.User {
    return []models.User{}
}
""")
    
    # models/user.go
    os.makedirs(f"{base}/models", exist_ok=True)
    with open(f"{base}/models/user.go", 'w') as f:
        f.write("""package models

type User struct {
    ID    uint   `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}
""")
    
    return base

def create_rust_project():
    """Crea proyecto Rust básico (CLI tool)"""
    base = "test_projects/rust_cli"
    os.makedirs(base, exist_ok=True)
    
    # Cargo.toml
    with open(f"{base}/Cargo.toml", 'w') as f:
        f.write("""[package]
name = "rust-cli"
version = "0.1.0"
edition = "2021"

[dependencies]
clap = "4.0"
serde = { version = "1.0", features = ["derive"] }
""")
    
    # src/main.rs
    os.makedirs(f"{base}/src", exist_ok=True)
    with open(f"{base}/src/main.rs", 'w') as f:
        f.write("""use clap::Parser;

mod commands;
mod models;

#[derive(Parser)]
struct Cli {
    #[arg(short, long)]
    input: String,
}

fn main() {
    let args = Cli::parse();
    commands::process(&args.input);
}
""")
    
    # src/commands.rs
    with open(f"{base}/src/commands.rs", 'w') as f:
        f.write("""pub fn process(input: &str) {
    println!("Processing: {}", input);
}
""")
    
    # src/models.rs
    with open(f"{base}/src/models.rs", 'w') as f:
        f.write("""use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
pub struct Data {
    pub value: String,
}
""")
    
    return base

def create_dotnet_project():
    """Crea proyecto .NET básico (Web API)"""
    base = "test_projects/dotnet_api"
    os.makedirs(base, exist_ok=True)
    
    # .csproj
    with open(f"{base}/DotNetApi.csproj", 'w') as f:
        f.write("""<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
  </ItemGroup>
</Project>
""")
    
    # Program.cs
    with open(f"{base}/Program.cs", 'w') as f:
        f.write("""using Microsoft.AspNetCore.Builder;
using DotNetApi.Controllers;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();

var app = builder.Build();
app.MapControllers();
app.Run();
""")
    
    # Controllers/UserController.cs
    os.makedirs(f"{base}/Controllers", exist_ok=True)
    with open(f"{base}/Controllers/UserController.cs", 'w') as f:
        f.write("""using Microsoft.AspNetCore.Mvc;

namespace DotNetApi.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class UserController : ControllerBase
    {
        [HttpGet]
        public IActionResult Get()
        {
            return Ok(new { message = "Users" });
        }
    }
}
""")
    
    # Models/User.cs
    os.makedirs(f"{base}/Models", exist_ok=True)
    with open(f"{base}/Models/User.cs", 'w') as f:
        f.write("""namespace DotNetApi.Models
{
    public class User
    {
        public int Id { get; set; }
        public string Name { get; set; }
    }
}
""")
    
    return base

def zip_project(project_path, output_name):
    """Comprime el proyecto en ZIP"""
    shutil.make_archive(f"uploads/{output_name}", 'zip', project_path)
    print(f"✅ Creado: uploads/{output_name}.zip")

def main():
    print("="*80)
    print("🏗️  GENERANDO PROYECTOS SINTÉTICOS PARA TESTING")
    print("="*80)
    
    os.makedirs("test_projects", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    print("\n📦 Creando proyectos...")
    
    # Go
    print("\n1. Go API REST...")
    go_path = create_go_project()
    zip_project(go_path, "go_api_test")
    
    # Rust
    print("\n2. Rust CLI Tool...")
    rust_path = create_rust_project()
    zip_project(rust_path, "rust_cli_test")
    
    # .NET
    print("\n3. .NET Web API...")
    dotnet_path = create_dotnet_project()
    zip_project(dotnet_path, "dotnet_api_test")
    
    print("\n" + "="*80)
    print("✅ PROYECTOS CREADOS")
    print("="*80)
    print("\nArchivos generados en uploads/:")
    print("  - go_api_test.zip")
    print("  - rust_cli_test.zip")
    print("  - dotnet_api_test.zip")
    
    print("\n💡 Ahora puedes ejecutar:")
    print("   python test_multiple_projects.py")

if __name__ == "__main__":
    main()
