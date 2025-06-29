# GitHub Environments Configuration for GOLEM

## 1. Create Environments

In GitHub repo settings → Environments, create:

### Development Environment
- Name: `development`
- Protection rules:
  - [ ] Required reviewers: 0
  - [ ] Wait timer: 0 minutes
  - [x] Deployment branches: Only `develop` branch

### Production Environment  
- Name: `production`
- Protection rules:
  - [x] Required reviewers: 1
  - [x] Wait timer: 5 minutes
  - [x] Deployment branches: Only `main` or `master` branch

## 2. Environment Secrets

### Development Secrets
```
DISCORD_TOKEN      = Your dev bot token
DOCKER_REGISTRY    = registry.example.com
DEPLOY_HOST        = dev.example.com
DEPLOY_USER        = deploy
SSH_PRIVATE_KEY    = Your dev SSH key
DISCORD_WEBHOOK    = Dev monitoring webhook
```

### Production Secrets
```
DISCORD_TOKEN      = Your PRODUCTION bot token (NEW ONE!)
DOCKER_REGISTRY    = registry.example.com
DEPLOY_HOST        = prod.example.com
DEPLOY_USER        = deploy
SSH_PRIVATE_KEY    = Your prod SSH key
DISCORD_WEBHOOK    = Prod monitoring webhook
DB_URL             = postgres://user:pass@host/golem
```

## 3. Update GitHub Actions

Update `.github/workflows/ci.yml` to use environments:

```yaml
deploy-dev:
  needs: build
  runs-on: ubuntu-latest
  environment: development
  if: github.ref == 'refs/heads/develop'
  steps:
    - name: Deploy to Dev
      env:
        DISCORD_TOKEN: ${{ secrets.DISCORD_TOKEN }}
        DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
      run: |
        echo "Deploying to development..."

deploy-prod:
  needs: build
  runs-on: ubuntu-latest
  environment: production
  if: github.ref == 'refs/heads/master'
  steps:
    - name: Deploy to Production
      env:
        DISCORD_TOKEN: ${{ secrets.DISCORD_TOKEN }}
        DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
      run: |
        echo "Deploying to production..."
```

## 4. Benefits

- **Separate secrets** per environment
- **Protection rules** for production
- **Deployment history** tracking
- **Manual approval** for production
- **Environment-specific** variables

## 5. Usage

After setup:
1. Push to `develop` → Auto-deploy to dev
2. Push to `master` → Requires approval → Deploy to prod
3. View deployments in repo → Deployments tab

## 6. Best Practices

- Always use environment secrets, not repo secrets
- Enable required reviewers for production
- Use wait timer to allow rollback window
- Keep production branch protected
- Monitor deployment history