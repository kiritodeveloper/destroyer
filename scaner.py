import nmap
import requests
import socket
import ssl
from urllib.parse import urlparse
import json
import time
from concurrent.futures import ThreadPoolExecutor

class ContainerOrchestratorScanner:
    def __init__(self, target):
        self.target = target
        self.open_ports = []
        self.services = {}
        self.vulnerabilities = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Puertos comunes para servicios de contenedores
        self.container_ports = [
            2375, 2376,  # Docker API
            9000, 9443,  # Portainer
            3000, 3001,  # Dokploy
            6443,        # Kubernetes API
            8080, 8443,  # Alternativas comunes
            5000,        # Docker Registry
            9090         # Prometheus (monitoreo)
        ]
        
        # Puertos comunes a escanear
        self.common_ports = [
            21, 22, 23, 53, 80, 110, 111, 135, 139, 143, 
            443, 993, 995, 1723, 3306, 3389, 5900, 8080
        ] + self.container_ports

    def scan_ports(self):
        """Escanea puertos usando nmap"""
        print(f"[*] Escaneando puertos en {self.target}...")
        
        nm = nmap.PortScanner()
        try:
            # Escaneo rápido de puertos específicos
            nm.scan(self.target, arguments=f"-p {','.join(map(str, self.common_ports))} -T4")
            
            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    for port in ports:
                        port_info = nm[host][proto][port]
                        if port_info['state'] == 'open':
                            self.open_ports.append(port)
                            self.services[port] = {
                                'service': port_info.get('name', 'unknown'),
                                'product': port_info.get('product', ''),
                                'version': port_info.get('version', ''),
                                'state': port_info['state']
                            }
            
            print(f"[+] Puertos abiertos encontrados: {self.open_ports}")
            return True
        except Exception as e:
            print(f"[-] Error en escaneo de puertos: {str(e)}")
            return False

    def detect_container_services(self):
        """Detecta servicios de gestión de contenedores"""
        print("[*] Detectando servicios de gestión de contenedores...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            for port in self.open_ports:
                executor.submit(self._check_port_service, port)
        
        time.sleep(2)  # Esperar a que terminen los hilos

    def _check_port_service(self, port):
        """Verifica qué servicio se ejecuta en un puerto específico"""
        try:
            # Verificar si es un servicio web
            if self._is_web_service(port):
                self._analyze_web_service(port)
            
            # Verificar si es Docker API
            elif port in [2375, 2376]:
                self._check_docker_api(port)
            
            # Verificar si es Kubernetes API
            elif port == 6443:
                self._check_kubernetes_api(port)
                
        except Exception as e:
            print(f"[-] Error verificando puerto {port}: {str(e)}")

    def _is_web_service(self, port):
        """Verifica si un puerto corre un servicio web"""
        try:
            url = f"http://{self.target}:{port}"
            response = self.session.get(url, timeout=5)
            return response.status_code < 500
        except:
            try:
                url = f"https://{self.target}:{port}"
                response = self.session.get(url, timeout=5, verify=False)
                return response.status_code < 500
            except:
                return False

    def _analyze_web_service(self, port):
        """Analiza servicios web en busca de Portainer/Dokploy"""
        protocols = ['http', 'https']
        
        for protocol in protocols:
            try:
                base_url = f"{protocol}://{self.target}:{port}"
                
                # Verificar Portainer
                if self._check_portainer(base_url):
                    self.services[port]['service'] = 'Portainer'
                    self.services[port]['url'] = base_url
                    self._check_portainer_vulnerabilities(base_url)
                    return
                
                # Verificar Dokploy
                if self._check_dokploy(base_url):
                    self.services[port]['service'] = 'Dokploy'
                    self.services[port]['url'] = base_url
                    self._check_dokploy_vulnerabilities(base_url)
                    return
                
                # Verificar otros servicios
                self._check_generic_web_service(base_url, port)
                    
            except Exception as e:
                continue

    def _check_portainer(self, base_url):
        """Verifica si el servicio es Portainer"""
        try:
            # Endpoint específico de Portainer
            response = self.session.get(f"{base_url}/api/endpoints", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        
        # Verificar título de página
        try:
            response = self.session.get(base_url, timeout=5)
            if "Portainer" in response.text:
                return True
        except:
            pass
        
        return False

    def _check_dokploy(self, base_url):
        """Verifica si el servicio es Dokploy"""
        try:
            # Endpoint específico de Dokploy
            response = self.session.get(f"{base_url}/api/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        
        # Verificar título de página
        try:
            response = self.session.get(base_url, timeout=5)
            if "Dokploy" in response.text:
                return True
        except:
            pass
        
        return False

    def _check_docker_api(self, port):
        """Verifica vulnerabilidades en Docker API"""
        try:
            url = f"http://{self.target}:{port}/version"
            if port == 2376:
                url = f"https://{self.target}:{port}/version"
            
            response = self.session.get(url, timeout=5, verify=False)
            if response.status_code == 200:
                docker_info = response.json()
                self.services[port]['service'] = 'Docker API'
                self.services[port]['version'] = docker_info.get('Version', 'unknown')
                
                # Verificar si requiere autenticación
                if 'ApiVersion' in docker_info:
                    self.vulnerabilities.append({
                        'port': port,
                        'service': 'Docker API',
                        'vulnerability': 'Docker API expuesta sin autenticación',
                        'severity': 'CRITICAL',
                        'description': 'El API de Docker está expuesta sin autenticación, permitiendo control total del host'
                    })
        except Exception as e:
            pass

    def _check_kubernetes_api(self, port):
        """Verifica vulnerabilidades en Kubernetes API"""
        try:
            url = f"https://{self.target}:{port}/version"
            response = self.session.get(url, timeout=5, verify=False)
            if response.status_code == 200:
                k8s_info = response.json()
                self.services[port]['service'] = 'Kubernetes API'
                self.services[port]['version'] = k8s_info.get('gitVersion', 'unknown')
                
                # Verificar acceso anónimo
                if response.headers.get('X-Kubernetes-Pf-Flowschema-Uid'):
                    self.vulnerabilities.append({
                        'port': port,
                        'service': 'Kubernetes API',
                        'vulnerability': 'Kubernetes API con acceso anónimo',
                        'severity': 'CRITICAL',
                        'description': 'La API de Kubernetes permite acceso anónimo, exponiendo todo el clúster'
                    })
        except Exception as e:
            pass

    def _check_portainer_vulnerabilities(self, base_url):
        """Verifica vulnerabilidades específicas de Portainer"""
        try:
            # Verificar si la API es accesible sin autenticación
            response = self.session.get(f"{base_url}/api/status", timeout=5)
            if response.status_code == 200:
                self.vulnerabilities.append({
                    'port': urlparse(base_url).port,
                    'service': 'Portainer',
                    'vulnerability': 'API de Portainer expuesta sin autenticación',
                    'severity': 'HIGH',
                    'description': 'La API de Portainer es accesible sin autenticación, permitiendo gestión de contenedores'
                })
        except:
            pass

    def _check_dokploy_vulnerabilities(self, base_url):
        """Verifica vulnerabilidades específicas de Dokploy"""
        try:
            # Verificar acceso a endpoints sensibles
            endpoints = [
                '/api/users',
                '/api/projects',
                '/api/applications'
            ]
            
            for endpoint in endpoints:
                response = self.session.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.vulnerabilities.append({
                        'port': urlparse(base_url).port,
                        'service': 'Dokploy',
                        'vulnerability': f'Endpoint sensible accesible: {endpoint}',
                        'severity': 'HIGH',
                        'description': f'El endpoint {endpoint} es accesible sin autenticación'
                    })
                    break
        except:
            pass

    def _check_generic_web_service(self, base_url, port):
        """Verifica vulnerabilidades en servicios web genéricos"""
        try:
            response = self.session.get(base_url, timeout=5)
            server_header = response.headers.get('Server', '')
            
            # Verificar información de servidor
            if server_header:
                self.services[port]['server'] = server_header
            
            # Verificar si expone información sensible
            if 'X-Powered-By' in response.headers:
                self.vulnerabilities.append({
                    'port': port,
                    'service': 'Web Service',
                    'vulnerability': 'Información de tecnología expuesta',
                    'severity': 'MEDIUM',
                    'description': f"Encabezado X-Powered-By revela: {response.headers['X-Powered-By']}"
                })
                
        except Exception as e:
            pass

    def generate_report(self):
        """Genera un reporte de hallazgos"""
        report = {
            'target': self.target,
            'scan_date': time.strftime("%Y-%m-%d %H:%M:%S"),
            'open_ports': self.open_ports,
            'services': self.services,
            'vulnerabilities': self.vulnerabilities,
            'summary': {
                'total_ports': len(self.open_ports),
                'container_services': len([s for s in self.services.values() if s['service'] in ['Portainer', 'Dokploy', 'Docker API', 'Kubernetes API']]),
                'critical_vulnerabilities': len([v for v in self.vulnerabilities if v['severity'] == 'CRITICAL']),
                'high_vulnerabilities': len([v for v in self.vulnerabilities if v['severity'] == 'HIGH'])
            }
        }
        
        print("\n" + "="*50)
        print("REPORTE DE ESCANEO")
        print("="*50)
        print(f"Objetivo: {self.target}")
        print(f"Puertos abiertos: {self.open_ports}")
        print(f"Servicios detectados: {len(self.services)}")
        print(f"Vulnerabilidades encontradas: {len(self.vulnerabilities)}")
        
        print("\nSERVICIOS DETECTADOS:")
        for port, info in self.services.items():
            print(f"  Puerto {port}: {info['service']} ({info.get('product', '')} {info.get('version', '')})")
        
        if self.vulnerabilities:
            print("\nVULNERABILIDADES:")
            for vuln in self.vulnerabilities:
                print(f"  [{vuln['severity']}] {vuln['vulnerability']} (Puerto {vuln['port']})")
                print(f"    Descripción: {vuln['description']}")
        
        print("\n" + "="*50)
        
        # Guardar reporte en JSON
        with open(f"scan_report_{self.target}_{int(time.time())}.json", 'w') as f:
            json.dump(report, f, indent=4)
        
        return report

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python scanner.py <subdominio>")
        sys.exit(1)
    
    target = sys.argv[1]
    
    # Validar formato de dominio
    if not target.startswith(('http://', 'https://')):
        target = f"http://{target}"
    
    parsed = urlparse(target)
    domain = parsed.netloc if parsed.netloc else parsed.path
    
    scanner = ContainerOrchestratorScanner(domain)
    
    if scanner.scan_ports():
        scanner.detect_container_services()
        scanner.generate_report()
    else:
        print("No se pudo completar el escaneo")

if __name__ == "__main__":
    main()





    #pip install python-nmap requests
    #python scanner.py subdominio.ejemplo.com