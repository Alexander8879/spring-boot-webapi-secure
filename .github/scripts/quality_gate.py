import json
import os
import sys

def evaluate_semgrep(report_path):
    failures = 0
    if not os.path.exists(report_path):
        print(f"[AVISO] No se encontro reporte Semgrep en: {report_path}")
        return failures

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo parsear {report_path}: {e}")
        return failures

    results = data.get("results", [])
    print(f"\n--- Evaluando Semgrep SAST ({len(results)} hallazgos totales) ---")
    for item in results:
        severity = item.get("extra", {}).get("severity", "").upper()
        rule_id = item.get("check_id")
        path = item.get("path")
        line = item.get("start", {}).get("line")

        if severity in ["ERROR", "CRITICAL", "HIGH"]:
            print(f"[FALLO SAST] [{severity}] {rule_id} -> {path}:{line}")
            failures += 1
        else:
            print(f"[INFO SAST] [{severity}] {rule_id} -> {path}:{line}")
    return failures

def evaluate_dependency_check(report_path):
    failures = 0
    if not os.path.exists(report_path):
        print(f"[AVISO] No se encontro reporte Dependency-Check en: {report_path}")
        return failures

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] No se pudo parsear {report_path}: {e}")
        return failures

    dependencies = data.get("dependencies", [])
    print(f"\n--- Evaluando OWASP Dependency-Check SCA ({len(dependencies)} dependencias analizadas) ---")
    for dep in dependencies:
        for vuln in dep.get("vulnerabilities", []):
            severity = vuln.get("severity", "").upper()
            cve = vuln.get("name")
            package = dep.get("fileName")
            cvss_v3 = vuln.get("cvssv3", {}).get("baseScore", 0.0)

            # Detecta vulnerabilidades criticas o altas (CVSS >= 7.0)
            if severity in ["CRITICAL", "HIGH"] or float(cvss_v3) >= 7.0:
                print(f"[FALLO SCA] [{severity} | CVSS {cvss_v3}] {cve} en {package}")
                failures += 1
    return failures

def main():
    semgrep_report = sys.argv[1] if len(sys.argv) > 1 else "semgrep-report.json"
    depcheck_report = sys.argv[2] if len(sys.argv) > 2 else "target/dependency-check-report.json"

    sast_fails = evaluate_semgrep(semgrep_report)
    sca_fails = evaluate_dependency_check(depcheck_report)
    total_failures = sast_fails + sca_fails

    print("\n" + "=" * 50)
    print("RESUMEN DEL QUALITY GATE:")
    print(f"- Fallos criticos/altos SAST (Semgrep): {sast_fails}")
    print(f"- Fallos criticos/altos SCA (OWASP DC): {sca_fails}")
    print("=" * 50)

    if total_failures > 0:
        print(f"\n[RECHAZADO] Quality Gate bloqueado: {total_failures} vulnerabilidades criticas o altas detectadas.")
        sys.exit(1)
    else:
        print("\n[APROBADO] Quality Gate exitoso: 0 vulnerabilidades criticas o altas.")
        sys.exit(0)

if __name__ == "__main__":
    main()