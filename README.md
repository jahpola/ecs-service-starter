# ECS Service Starter

A CLI tool to start and stop ECS services.

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

AWS credentials must be configured via the standard AWS config chain (environment variables, `~/.aws/credentials`, IAM role, etc.).

## Usage

```bash
uv run main.py --cluster <cluster-name> --service <service-name> --stop|--start
```

### Stop a single service

```bash
uv run main.py --cluster my-cluster --service my-service --stop
```

### Start a single service

```bash
uv run main.py --cluster my-cluster --service my-service --start
```

### Stop all services in a cluster

```bash
uv run main.py --cluster my-cluster --all --stop
```

### Start all services in a cluster

```bash
uv run main.py --cluster my-cluster --all --start
```

### Verbose output

Add `--verbose` to enable debug logging:

```bash
uv run main.py --cluster my-cluster --all --stop --verbose
```

## Development

```bash
uv sync --group dev
uv run ruff check .
uv run ty check .
```
