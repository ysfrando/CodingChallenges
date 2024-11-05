import requests
import json
import sys
import pkg_resources
from packaging import version
import os
import re

def get_dependencies(requirements_file):
    dependencies = {}
    try:
        with open(requirements_file, 'r') as f:
            for line in f:
                if '==' in line:
                    name, ver = line.strip().split('==')
                    dependencies[name] = ver
    except FileNotFoundError:
        print(f"Error: {requirements_file} not found")
        sys.exit(1)
    return dependencies

def check_vulnerability(package_name, package_version):
    url = "https://api.osv.dev/v1/query"
    
    payload = {
        "package": {
            "name": package_name,
            "ecosystem": "PyPI"
        },
        "version": package_version
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get('vulns', [])
    except requests.exceptions.RequestException as e:
        print(f"Error querying OSV API: {str(e)}")
        return []

def parse_cvss_score(cvss_string):
    # Extract the base score from a CVSS v3 vector string
    match = re.search(r'/(\d+\.\d+)/', cvss_string)
    if match:
        return float(match.group(1))
    return 0.0

def generate_report(vulnerabilities):
    if not os.path.exists('security_reports'):
        os.makedirs('security_reports')
        
    report_file = 'security_reports/vulnerability_report.json'
    with open(report_file, 'w') as f:
        json.dump(vulnerabilities, f, indent=2)
    
    # Generate summary
    total_vulns = sum(len(vulns) for vulns in vulnerabilities.values())
    critical_vulns = sum(
        1 for vulns in vulnerabilities.values()
        for vuln in vulns
        if isinstance(vuln, dict) and 'severity' in vuln and 
        (
            (isinstance(vuln['severity'], list) and any(parse_cvss_score(sev.get('score', '0.0')) >= 9.0 for sev in vuln['severity'] if isinstance(sev, dict))) or
            (isinstance(vuln['severity'], str) and vuln['severity'].lower() in ['critical', 'high']) or
            (isinstance(vuln['severity'], dict) and parse_cvss_score(vuln['severity'].get('score', '0.0')) >= 9.0)
        )
    )
    
    return {
        'total_packages': len(vulnerabilities),
        'total_vulnerabilities': total_vulns,
        'critical_vulnerabilities': critical_vulns,
        'report_location': report_file
    }


def main():
    requirements_file = 'requirements.txt'
    dependencies = get_dependencies(requirements_file)
    
    vulnerability_findings = {}
    
    for package, ver in dependencies.items():
        print(f"Checking {package} version {ver}...")
        vulns = check_vulnerability(package, ver)
        if vulns:
            vulnerability_findings[package] = vulns
    
    summary = generate_report(vulnerability_findings)
    
    print("\nScan Complete!")
    print(f"Total packages scanned: {summary['total_packages']}")
    print(f"Total vulnerabilities found: {summary['total_vulnerabilities']}")
    print(f"Critical vulnerabilities: {summary['critical_vulnerabilities']}")
    print(f"Detailed report saved to: {summary['report_location']}")

if __name__ == "__main__":
    main()
