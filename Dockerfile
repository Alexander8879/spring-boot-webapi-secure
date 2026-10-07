# ---- Build stage ----
FROM maven:3.9.11-eclipse-temurin-21 AS builder

WORKDIR /app

# Copy pom first (better layer caching)
COPY pom.xml .

# Download dependencies (cached unless pom changes)
RUN mvn dependency:go-offline -B

# Copy source and build
COPY src src
RUN mvn package -DskipTests -B


# ---- Runtime stage ----
FROM eclipse-temurin:21-jre-alpine

# Install curl for healthcheck and create non-root user
RUN apk add --no-cache curl \
    && addgroup -S spring \
    && adduser -S spring -G spring

WORKDIR /app

# Copy only the fat jar
COPY --from=builder /app/target/*.jar app.jar

# Security: run as non-root user
USER spring:spring

# Expose application port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]