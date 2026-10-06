# Lab 4 — SBOM Maven con CycloneDX y análisis SCA con Trivy

## 1. Objetivo

Generar un SBOM (Software Bill of Materials) del proyecto Maven mediante CycloneDX y realizar un análisis SCA con Trivy para identificar vulnerabilidades conocidas presentes en las dependencias de la aplicación.

El análisis se realizó sin iniciar la aplicación Spring Boot, utilizando el inventario de componentes generado a partir de las dependencias Maven.

---

## 2. Proyecto analizado

Aplicación:

- Nombre: `springboot-devsecops-lab`
- Versión: `1.0.0`
- Tipo: aplicación Java / Spring Boot
- Java: 21
- Formato del SBOM: CycloneDX
- Versión del esquema: 1.6
- Trivy: 0.74.0

PURL de la aplicación:

`pkg:maven/bo.edu.devsecops/springboot-devsecops-lab@1.0.0?type=jar`

---

## 3. Revisión del SBOM

El SBOM permitió identificar los componentes utilizados por la aplicación, incluyendo dependencias directas y transitivas.

### Dependencia directa analizada

- Nombre: `commons-text`
- Grupo: `org.apache.commons`
- Versión inicial: `1.9`
- PURL: `pkg:maven/org.apache.commons/commons-text@1.9?type=jar`

### Dependencia transitiva observada

- Nombre: `commons-lang3`
- Grupo: `org.apache.commons`
- Versión: `3.17.0`
- PURL: `pkg:maven/org.apache.commons/commons-lang3@3.17.0?type=jar`

El SBOM inicial fue conservado como:

`reports/bom-before.json`

---

## 4. Análisis SCA inicial

Se ejecutó Trivy sobre el SBOM inicial y el resultado fue almacenado en:

`reports/sca-before.json`

Durante el análisis se identificó una vulnerabilidad crítica asociada con Apache Commons Text.

### Hallazgo seleccionado

- Componente: `org.apache.commons:commons-text`
- CVE: `CVE-2022-42889`
- Severidad: `CRITICAL`
- Versión instalada: `1.9`
- Versión corregida mínima indicada por el reporte: `1.10.0`
- Estado reportado: `fixed`

El análisis confirmó que la versión `1.9` utilizada por el proyecto se encontraba dentro del rango afectado por la vulnerabilidad.

---

## 5. Riesgo identificado

La vulnerabilidad `CVE-2022-42889` afecta a determinadas versiones de Apache Commons Text relacionadas con el mecanismo de interpolación de variables.

El reporte SCA permitió identificar que el proyecto utilizaba la versión vulnerable `1.9`.

La presencia de una dependencia vulnerable no demuestra por sí sola que un endpoint de la aplicación sea explotable, ya que también debe analizarse cómo utiliza la aplicación dicha biblioteca. Sin embargo, la existencia de una versión corregida justifica la actualización del componente para reducir la exposición.

---

## 6. Corrección aplicada

Se modificó la dependencia directa en el archivo `pom.xml`.

### Antes

```xml
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-text</artifactId>
    <version>1.9</version>
</dependency>
```

### Después

```xml
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-text</artifactId>
    <version>1.10.0</version>
</dependency>
```