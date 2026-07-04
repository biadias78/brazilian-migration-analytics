# Brazilian Migration Analytics Pipeline

This project is a containerized data engineering pipeline designed to process and analyze Brazilian migration data. It leverages **Python 3.13**, **DuckDB** for lightning-fast local analytics storage, and **dbt (data build tool)** for data transformation modeling.

---

## 🛠️ Tech Stack & Prerequisites

* **Language:** Python 3.13 (Slim-Linux base)


* **Database & Transformation:** DuckDB + `dbt-duckdb`

* **Orchestration & Processing:** Pandas, NumPy, Requests


* **Containerization:** Docker & Docker Compose



### Prerequisites

Ensure you have the following installed on your host machine:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine with Compose plugin)


* [VS Code](https://code.visualstudio.com/) with the **Dev Containers** extension (optional, for containerized development)



---

## 🚀 Getting Started

### 1. Project Setup

Clone this repository to your local machine and navigate into the root directory:

```bash
cd brazilian-migration-analytics

```

### 2. Launch the Environment

Use Docker Compose to build the image and spin up the background container. This automatically mounts your local workspace into the container at `/app`:

```bash
docker compose up -d --build
```

---

## 🏃‍♂️ Running the Pipeline

Once the container is up and running, you can execute commands directly inside it using `docker compose exec`.

### Run the Main Python Pipeline

To run the full ingestion and execution sequence defined in your source code:

```bash
docker compose exec brazil-analytics python -m src.main all
```

or you can attach the shell to the docker container manually then run:

```bash
python -m src.main all
```

### Run dbt Models

Because the environment is pre-configured with `dbt-duckdb`, you can execute dbt commands seamlessly:

* **Check dbt version and connection:**

```bash
docker compose exec brazil-analytics dbt --version

```


* **Run data transformation models:**

```bash
docker compose exec brazil-analytics dbt run

```


* **Test data quality:**

```bash
docker compose exec brazil-analytics dbt test

```

### Run Jupyter Notebook
```bash
docker compose exec brazil-analytics jupyter lab --ip 0.0.0.0 --port 8888 --no-browser --allow-root
```

### Interactive Debugging (Shell Access)

If you need to explore files or run ad-hoc scripts inside the isolated Linux environment, open a bash session:

```bash
docker compose exec brazil-analytics bash

```

---

## 🧹 Maintenance & Reset Commands

Use these commands to manage, stop, or completely refresh your Docker environment.

### Stop the Container

To stop the environment without deleting images or data:

```bash
docker compose stop

```

### Start Clean (Full Reset)

If you modify the `Dockerfile`, update packages, or want to wipe out the environment to start completely fresh, execute the following block:

```bash
# 1. Bring down the container and associated networks
docker compose down

# 2. Remove the project image
docker rmi brazilian-migration-analytics:latest

# 3. Clear out unused Docker build cache to force a fresh pull
docker builder prune -f

```