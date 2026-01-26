# DNS Updates Required for Cloudflare

## Status Update

✅ **Working Domains:**
- `yennefer.quest` - Main portal
- `api.yennefer.quest` - Soul API
- `yennefer.genesisconductor.io` - Landing page
- `soul.genesisconductor.io` - Soul state API
- `vault.genesisconductor.io` - Now routing correctly (HTTP 200)

## Required DNS Updates

### 1. vault.yennefer.quest (NEW CNAME)

**Status:** DNS record doesn't exist yet

**Action Required:**
1. Log into Cloudflare dashboard
2. Navigate to DNS settings for `yennefer.quest`
3. Add new CNAME record:
   - **Type:** CNAME
   - **Name:** `vault`
   - **Target:** `ed8b80e3-0634-4933-a722-94d4cae6205c.cfargotunnel.com`
   - **Proxy status:** Proxied (orange cloud)
   - **TTL:** Auto

**Expected Result:**
- `https://vault.yennefer.quest` → Diamond Vault dashboard (port 8100)

---

### 2. vault.genesisconductor.io (UPDATE EXISTING)

**Status:** CNAME currently points to wrong tunnel

**Current Configuration:**
- Points to old/incorrect tunnel ID

**Action Required:**
1. Log into Cloudflare dashboard
2. Navigate to DNS settings for `genesisconductor.io`
3. Update existing CNAME record for `vault`:
   - **Type:** CNAME
   - **Name:** `vault`
   - **Target:** `ed8b80e3-0634-4933-a722-94d4cae6205c.cfargotunnel.com`
   - **Proxy status:** Proxied (orange cloud)
   - **TTL:** Auto

**Note:** This domain is currently working (HTTP 200), but ensure tunnel ID matches for consistency.

---

### 3. a2a.genesisconductor.io (VERIFY/CREATE)

**Status:** May need verification or creation

**Action Required:**
1. Verify if CNAME exists for `a2a.genesisconductor.io`
2. If missing, create new CNAME:
   - **Type:** CNAME
   - **Name:** `a2a`
   - **Target:** `ed8b80e3-0634-4933-a722-94d4cae6205c.cfargotunnel.com`
   - **Proxy status:** Proxied (orange cloud)
   - **TTL:** Auto

**Expected Result:**
- `https://a2a.genesisconductor.io` → A2A Handoff server (port 8200)

---

## Cloudflare Tunnel Configuration

**Tunnel ID:** `ed8b80e3-0634-4933-a722-94d4cae6205c`

**Ingress Rules (verify these are configured in tunnel):**

```yaml
ingress:
  - hostname: vault.yennefer.quest
    service: http://localhost:8100
  - hostname: vault.genesisconductor.io
    service: http://localhost:8100
  - hostname: a2a.genesisconductor.io
    service: http://localhost:8200
  - hostname: yennefer.quest
    service: http://localhost:8000
  - hostname: api.yennefer.quest
    service: http://localhost:8088
  - hostname: yennefer.genesisconductor.io
    service: http://localhost:8000
  - hostname: soul.genesisconductor.io
    service: http://localhost:8088
  - service: http_status:404
```

---

## Verification Steps

After making DNS changes, verify with:

```bash
# Test vault.yennefer.quest
curl -s https://vault.yennefer.quest/health | jq .

# Test a2a.genesisconductor.io
curl -s https://a2a.genesisconductor.io/health | jq .

# Test quantum operation
curl -s -X POST https://vault.yennefer.quest/api/quantum/QUANTUM_BREATHE \
  -H "Content-Type: application/json" -d '{}' | jq .
```

---

## Notes

- DNS propagation may take up to 48 hours (usually 5-15 minutes with Cloudflare)
- All domains use Cloudflare proxy (orange cloud) for DDoS protection and caching
- Tunnel `ed8b80e3-0634-4933-a722-94d4cae6205c` must be running for domains to resolve
- Verify tunnel is active: `cloudflared tunnel list`
