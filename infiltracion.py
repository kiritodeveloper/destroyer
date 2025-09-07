import nmap
import socket
import sys
from datetime import datetime
import json

def scan_subdomain(subdomain):
    """
    Realiza un escaneo de puertos a un subdominio específico
    """
    print(f"[*] Iniciando escaneo de puertos para: {subdomain}")
    print(f"[*] Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar si el dominio existe
    try:
        ip = socket.gethostbyname(subdomain)
        print(f"[+] Dirección IP resuelta: {ip}")
    except socket.gaierror:
        print(f"[-] Error: No se pudo resolver el dominio {subdomain}")
        return None
    
    # Inicializar escaner nmap
    nm = nmap.PortScanner()
    
    # Puertos comunes a escanear
    common_ports = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
        143, 443, 993, 995, 1723, 3306, 3389, 5432,
        5900, 6379, 8080, 8443, 8888, 9200, 27017
    ]
    
    # Puertos específicos para servicios web y de contenedores
    container_ports = [
        2375, 2376,  # Docker API
        9000, 9443,  # Portainer
        3000, 3001,  # Dokploy
        6443,        # Kubernetes API
        5000,        # Docker Registry
        9090         # Prometheus
    ]
    
    # Combinar todos los puertos
    ports_to_scan = list(set(common_ports + container_ports))
    
    print(f"[*] Escaneando {len(ports_to_scan)} puertos...")
    
    try:
        # Realizar escaneo de puertos
        nm.scan(subdomain, arguments=f"-p {','.join(map(str, ports_to_scan))} -sV -T4")
        
        # Procesar resultados
        results = {
            'subdomain': subdomain,
            'ip': ip,
            'scan_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'open_ports': [],
            'closed_ports': [],
            'filtered_ports': [],
            'services': {}
        }
        
        if subdomain in nm.all_hosts():
            host = nm[subdomain]
            
            for proto in host.all_protocols():
                ports = host[proto].keys()
                
                for port in ports:
                    port_info = host[proto][port]
                    state = port_info['state']
                    
                    if state == 'open':
                        results['open_ports'].append(port)
                        results['services'][port] = {
                            'service': port_info.get('name', 'unknown'),
                            'product': port_info.get('product', ''),
                            'version': port_info.get('version', ''),
                            'extra_info': port_info.get('extrainfo', '')
                        }
                        print(f"[+] Puerto {port} ({port_info['name']}) - ABIERTO")
                    elif state == 'closed':
                        results['closed_ports'].append(port)
                    elif state == 'filtered':
                        results['filtered_ports'].append(port)
        
        # Generar reporte
        generate_report(results)
        return results
        
    except Exception as e:
        print(f"[-] Error durante el escaneo: {str(e)}")
        return None

def generate_report(results):
    """
    Genera un reporte en formato JSON y muestra un resumen
    """
    if not results:
        print("[-] No se generó reporte")
        return
    
    # Mostrar resumen
    print("\n" + "="*50)
    print("REPORTE DE ESCANEO DE PUERTOS")
    print("="*50)
    print(f"Subdominio: {results['subdomain']}")
    print(f"IP: {results['ip']}")
    print(f"Fecha: {results['scan_date']}")
    print(f"Puertos abiertos: {len(results['open_ports'])}")
    print(f"Puertos cerrados: {len(results['closed_ports'])}")
    print(f"Puertos filtrados: {len(results['filtered_ports'])}")
    
    if results['open_ports']:
        print("\nPUERTOS ABIERTOS:")
        for port in sorted(results['open_ports']):
            service = results['services'][port]
            print(f"  {port}/tcp - {service['service']} {service['product']} {service['version']} {service['extra_info']}")
    
    # Guardar reporte en JSON
    filename = f"scan_report_{results['subdomain'].replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)
    
    print(f"\n[+] Reporte guardado en: {filename}")
    print("="*50)

def main():
    if len(sys.argv) != 2:
        print("Uso: python scan_ports.py <subdominio>")
        print("Ejemplo: python scan_ports.py uatf.edu.bo")
        sys.exit(1)
    
    subdomain = sys.argv[1]
    scan_subdomain(subdomain)

if __name__ == "__main__":
    main()