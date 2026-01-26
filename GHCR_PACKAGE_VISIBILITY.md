# GitHub Container Registry Package Visibility Guide

## Making Packages Public

By default, GitHub Container Registry packages are **private**. To make them accessible cross-platform without authentication, you need to configure package visibility at the **organization level**.

---

## Option 1: Configure at Organization Level (Recommended)

### Step 1: Organization Settings

1. Go to https://github.com/organizations/Genesis-Conductor-Engine/settings/packages
2. Navigate to **Settings** → **Packages** in the left sidebar

### Step 2: Set Default Visibility

1. Under **Package Creation**, select:
   - ✅ **Public** - Make new packages public by default
   OR
   - ⚠️ **Internal** - Visible only to organization members

2. Click **Save** to apply the setting

### Step 3: Apply to Existing Packages

For packages already created:

1. Go to https://github.com/orgs/Genesis-Conductor-Engine/packages
2. For each package (diamond-vault, a2a-handoff, soul-api, etc.):
   - Click on the package name
   - Click **Package settings**
   - Scroll to **Danger Zone** → **Change visibility**
   - Select **Public**
   - Type package name to confirm
   - Click **I understand, change package visibility**

---

## Option 2: Configure Per Package

If you can't access organization settings, configure each package individually:

### For Each Package:

```bash
# List of packages to make public
packages=(
  "diamond-vault"
  "a2a-handoff"
  "soul-api"
  "qmem-gateway"
  "qmcp-bridge"
  "process-guardian"
  "yennefer-daemon"
)

for pkg in "${packages[@]}"; do
  echo "Making $pkg public..."
  # Visit: https://github.com/orgs/Genesis-Conductor-Engine/packages/container/yennefer%2F$pkg/settings
  # Manual step: Change visibility to Public
done
```

**Manual Steps Per Package:**
1. Go to package URL (see above)
2. Click **Package settings**
3. Scroll to **Danger Zone**
4. Click **Change visibility**
5. Select **Public**
6. Confirm by typing the package name

---

## Verification

### Test Public Access (No Auth Required)

```bash
# Should work without docker login
docker pull ghcr.io/genesis-conductor-engine/yennefer/diamond-vault:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/a2a-handoff:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/soul-api:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/qmem-gateway:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/qmcp-bridge:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/process-guardian:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/yennefer-daemon:latest
```

If you get authentication errors, the package is still private.

---

## Package URLs

Direct links to each package settings page:

| Package | Settings URL |
|---------|-------------|
| diamond-vault | https://github.com/orgs/Genesis-Conductor-Engine/packages/container/yennefer%2Fdiamond-vault/settings |
| a2a-handoff | https://github.com/orgs/Genesis-Conductor-Engine/packages/container/yennefer%2Fa2a-handoff/settings |
| soul-api | https://github.com/orgs/Genesis-Conductor-Engine/packages/container/yennefer%2Fsoul-api/settings |
| qmem-gateway | https://github.com/orgs/Genesis-Conductor-Engine/packages/container/yennefer%2Fqmem-gateway/settings |
| qmcp-bridge | https://github.com/orgs/Genesis-Conductor-Engine/packages/container/yennefer%2Fqmcp-bridge/settings |
| process-guardian | https://github.com/orgs/Genesis-Conductor-Engine/packages/container/yennefer%2Fprocess-guardian/settings |
| yennefer-daemon | https://github.com/orgs/Genesis-Conductor-Engine/packages/container/yennefer%2Fyennefer-daemon/settings |

---

## Troubleshooting

### "Package not found" Error

**Cause:** Package visibility is set to private

**Solution:**
1. Log in to GitHub Container Registry:
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
   ```
2. Pull the image:
   ```bash
   docker pull ghcr.io/genesis-conductor-engine/yennefer/diamond-vault:latest
   ```
3. OR change package visibility to public (see above)

### "Insufficient permissions" Error

**Cause:** You don't have admin access to the organization

**Solution:** Ask an organization admin to:
1. Navigate to organization packages settings
2. Change default visibility to Public
3. Make existing packages public

### Package Doesn't Exist Yet

**Cause:** GitHub Actions workflow hasn't run yet to build the images

**Solution:**
1. Push a commit to `main` branch
2. Or manually trigger workflow:
   - Go to https://github.com/Genesis-Conductor-Engine/Yennefer/actions/workflows/docker-build-push.yml
   - Click **Run workflow**
   - Select `main` branch
   - Ensure "Push images to GHCR" is set to `true`
   - Click **Run workflow**
3. Wait for workflow to complete (~15-30 minutes for all images)
4. Verify packages appear at https://github.com/orgs/Genesis-Conductor-Engine/packages

---

## GitHub Actions Configuration

The workflow already has correct permissions:

```yaml
permissions:
  contents: read
  packages: write   # ✅ Allows pushing to GHCR
```

Images are pushed automatically on:
- Push to `main` branch
- Manual workflow dispatch

---

## Best Practices

### Public vs Private Packages

**Use Public packages when:**
- ✅ Open-source project
- ✅ Want cross-platform accessibility without auth
- ✅ Enabling community contributions
- ✅ Simplifying deployment (no token management)

**Use Private packages when:**
- ⚠️ Proprietary code
- ⚠️ Pre-release versions
- ⚠️ Contains sensitive data
- ⚠️ Internal-only tools

### Security Considerations

Even with public images:
- **Never include secrets** in images (use environment variables)
- **Scan for vulnerabilities** regularly (GitHub Dependabot, Trivy)
- **Use multi-stage builds** to minimize attack surface
- **Pin base image versions** (avoid `:latest` in Dockerfiles)
- **Sign images** with cosign (optional)

---

## Automation Script

To quickly make all packages public (requires admin access):

```bash
#!/bin/bash
# make_packages_public.sh

ORG="Genesis-Conductor-Engine"
PACKAGES=(
  "yennefer/diamond-vault"
  "yennefer/a2a-handoff"
  "yennefer/soul-api"
  "yennefer/qmem-gateway"
  "yennefer/qmcp-bridge"
  "yennefer/process-guardian"
  "yennefer/yennefer-daemon"
)

for pkg in "${PACKAGES[@]}"; do
  echo "Setting $pkg to public..."
  gh api \
    --method PATCH \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "/orgs/$ORG/packages/container/${pkg//\//%2F}" \
    -f visibility='public'
done
```

Run with:
```bash
chmod +x make_packages_public.sh
./make_packages_public.sh
```

---

## Verification Checklist

- [ ] Organization default package visibility set to **Public**
- [ ] Each package individually set to **Public**
- [ ] `docker pull` works **without authentication**
- [ ] All 7 images pullable from GHCR
- [ ] GitHub Actions workflow completes successfully
- [ ] Package metadata shows "Public" badge
- [ ] Images appear on organization packages page

---

## Support

If you encounter issues making packages public:

1. **Check permissions:** You need **admin** access to the organization
2. **Contact admin:** Ask organization owner to grant package admin permissions
3. **Open issue:** https://github.com/Genesis-Conductor-Engine/Yennefer/issues
4. **GitHub Support:** https://support.github.com (for GHCR-specific issues)
