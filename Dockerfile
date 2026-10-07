# ---- Build stage ----
FROM maven:3.9.11-eclipse-temurin-21 AS builder

WORKDIR /app

# Copiar archivos necesarios para compilar
COPY pom.xml .
COPY src ./src

# Compilar la aplicación
RUN mvn -B --no-transfer-progress clean package -DskipTests

# Seleccionar únicamente el JAR ejecutable
RUN JAR_FILE=$(find target -maxdepth 1 -type f \
    -name "*.jar" ! -name "original-*" | head -n 1) \
    && test -n "$JAR_FILE" \
    && cp "$JAR_FILE" target/app.jar


# ---- Runtime stage ----
FROM eclipse-temurin:21-jre-alpine

# Curl para healthcheck y usuario sin privilegios
RUN apk add --no-cache curl \
    && addgroup -S spring \
    && adduser -S spring -G spring

WORKDIR /app

# Copiar únicamente el JAR construido
COPY --from=builder /app/target/app.jar app.jar

# Ejecutar como usuario no root
USER spring:spring

EXPOSE 8080

# Verificar estado de la aplicación
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]