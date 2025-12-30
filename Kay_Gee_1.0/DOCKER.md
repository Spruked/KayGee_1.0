# KayGee 1.0 - Docker Deployment Guide

## Quick Start

### Build and Run
```bash
# Build the image
docker build -t kaygee:1.0 .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f kaygee

# Stop
docker-compose down
```

### Run Single Container
```bash
# Run KayGee main system
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config.yaml:/app/config.yaml \
  kaygee:1.0

# Run Dashboard
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  kaygee:1.0 python dashboard/kg_voice_dashboard.py

# Run Tests
docker run -it --rm kaygee:1.0 python -m pytest tests/ -v
```

## Data Persistence

All data is persisted in volumes:
- `./data/` - Vaults, sessions, Merkle trees
- `./logs/` - System logs
- `./config.yaml` - Configuration

## Development Mode

```bash
# Run with code mounted for live development
docker run -it --rm \
  -v $(pwd):/app \
  kaygee:1.0 bash

# Then inside container
python main.py
```

## Production Deployment

### Environment Variables
- `KAYGEE_ENV` - Set to `production`
- `KAYGEE_DATA_DIR` - Data directory path
- `KAYGEE_LOG_DIR` - Log directory path

### Security
- Review `config.yaml` security settings
- Set proper file permissions on data volumes
- Use secrets management for sensitive configs

## Monitoring

```bash
# Check container health
docker ps
docker inspect kaygee-1.0

# View resource usage
docker stats kaygee-1.0

# Access logs
docker logs kaygee-1.0 -f
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker logs kaygee-1.0

# Verify image built correctly
docker images | grep kaygee

# Check data directory permissions
ls -la data/
```

### Import errors
```bash
# Rebuild image
docker-compose build --no-cache
```

### Data not persisting
```bash
# Verify volume mounts
docker inspect kaygee-1.0 | grep Mounts -A 10
```

## Backup

```bash
# Backup all data
tar -czf kaygee-backup-$(date +%Y%m%d).tar.gz data/ logs/ config.yaml

# Restore
tar -xzf kaygee-backup-YYYYMMDD.tar.gz
```
