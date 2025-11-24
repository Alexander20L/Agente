from core.analyzer import analyze_project
r = analyze_project('spring-petclinic.zip')
print(f"PageRank disponible: {len(r.get('important_components', []))} componentes")
if r.get('important_components'):
    print("\nTop 5 por PageRank:")
    for i, c in enumerate(r['important_components'][:5], 1):
        print(f"  {i}. {c['component']} (score: {c['pagerank']:.4f})")
