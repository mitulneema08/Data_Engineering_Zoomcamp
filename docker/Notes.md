# Docker Notes — Module 1
*Data Engineering Zoomcamp*
*Last Updated: April 2026*

---

## Key Concepts

### Docker Image
- A blueprint/recipe — read-only, never changes
- Contains: OS libs, runtime (Python), dependencies, your code
- Built once, reused forever
- Analogy: Ford vehicle spec sheet locked in a vault

### Docker Container
- A running instance created FROM an image
- Disposable — start it, use it, throw it away
- Many containers can run from one image simultaneously
- Analogy: Actual car built from the spec sheet

### Writable Layer
- Added on top of image layers when container runs
- EPHEMERAL — completely gone when container stops
- Analogy: Scratches on a car don't change the spec sheet

### Volume
- A folder mounted from outside the container into the container
- Survives container stop/crash/deletion
- Zero extra space — it is a direct link, not a copy
- Syntax: -v /host/path:/container/path
- Analogy: Saving work to a shared drive instead of inside the car

---

## One-Line Summary
Image = recipe | Container = meal cooked from it | Writable layer = dirty dishes | Volume = Tupperware that saves leftovers

---

## Key Commands

### Basic Container Commands
docker run hello-world                  # test Docker is working
docker run ubuntu                       # starts and exits immediately
docker run -it ubuntu                   # interactive terminal = bash shell
docker run -it --rm ubuntu              # auto-deletes container on exit

### Cleanup Commands
docker ps -a                            # list all containers including dead ones
docker rm $(docker ps -aq)             # remove ALL stopped containers

### Volume Mount
docker run -it \
    --rm \
    -v $(pwd)/test:/app/test \
    --entrypoint=bash \
    python:3.9.16-slim

### Build Your Own Image
docker build -t image-name:tag .        # build image from Dockerfile
docker run -it image-name:tag 10        # run container passing argument

---

## Dockerfile — Simple (pip)

FROM python:3.13.11-slim        # base image to build on
RUN pip install pandas pyarrow  # install dependencies during build
WORKDIR /app                    # set working directory inside container
COPY pipeline.py pipeline.py    # bake script into image permanently
ENTRYPOINT ["python", "pipeline.py"]  # run automatically on start

## Dockerfile — Production (uv)

FROM python:3.13.10-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
COPY "pyproject.toml" "uv.lock" ".python-version" ./
RUN uv sync --locked
COPY pipeline.py pipeline.py
ENTRYPOINT ["uv", "run", "python", "pipeline.py"]

---

## Virtual Environments (uv)

### Why Virtual Environments?
- Each project gets isolated Python + libraries
- No conflicts between projects
- Reproducible — same environment everywhere

### uv Commands
pip install uv                  # install uv itself
uv init --python=3.13           # create new project with Python 3.13
uv add pandas pyarrow           # add dependencies to pyproject.toml
uv run python pipeline.py 10    # run using project virtual environment
uv run which python             # shows project isolated Python path
which python                    # shows system Python path

---

## Layer Caching — Important Optimization
- Copy dependency files BEFORE code files in Dockerfile
- Code changes only rebuild the code layer not dependencies
- Saves huge time on GCP when rebuilding images

---

## slim vs full images
- python:3.9.16       = 924MB  full version with compilers
- python:3.9.16-slim  = 131MB  only what is needed to run
- Use slim in production — cheaper and faster on GCP

---

## Real World DE Connection (Ford)
Container = disposable worker sent on a task
Volume = GCS bucket where pipeline output lands
Image = packaged reproducible pipeline environment

Pipeline flow:
NHTSA API → Container with volume mount → GCS Bucket → BigQuery

---

## gitignore Entries
*.parquet       # binary output files never commit
.venv/          # virtual environment never commit
__pycache__/    # Python cache never commit
*.pyc