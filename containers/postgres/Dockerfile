# Use the official PostgreSQL image as the base image
FROM postgres:latest

# Copy the SQL script to initialize the database
COPY ./containers/postgres/init.sql /docker-entrypoint-initdb.d/

# Expose the default PostgreSQL port
EXPOSE 5432

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD pg_isready -U postgres
