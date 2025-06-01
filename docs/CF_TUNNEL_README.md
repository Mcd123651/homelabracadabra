🡐[🧙‍♂️ homelabracadabra](../README.md)

# Guide to Setting Up a Cloudflare Tunnel with Custom Domain and Zero Trust

This guide walks you through setting up a Cloudflare Tunnel to securely expose your internal service (e.g., swag reverse proxy) through a custom domain with Cloudflare Zero Trust.

---

## 1. Set Up a Custom Domain in Cloudflare

- Register or transfer your domain to Cloudflare, or add an existing domain.
- Once added, update your domain registrar’s nameservers to point to the **Cloudflare Nameservers** provided.
- Wait for DNS propagation and ensure your domain is active and managed by Cloudflare.

---

## 2. Set Up a Cloudflare Zero Trust Dashboard

- Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) dashboard.
- Create an account or log in.
- Zero Trust is free but **requires credit card info** for verification.
- Complete initial setup (organization name, etc.) as prompted.

---

## 3. Create a Cloudflare Tunnel

- In the Zero Trust dashboard, navigate to **Access > Tunnels** (sometimes under **Networks > Tunnels**).
- Click **Create Tunnel**.
- Name your tunnel after your domain, e.g., `domain.com`.
- When creating the tunnel, **capture and save the generated token** securely — you will need it to authenticate the tunnel agent.

---

## 4. Set Public Hostnames

- Still in the tunnel configuration, define **two public hostnames**:
  - `domain.com`
  - `*.domain.com` (wildcard for subdomains)

These hostnames are the publicly accessible URLs routed through the tunnel.
This will automatically add the DNS records for wildcard.

---

## 5. Configure the Service

- For each hostname, set the **service type to HTTPS**.
- Point the service URL to your internal reverse proxy, e.g.: ```swag:443```

This assumes your internal service `swag` is listening on port ``443``.

---

## 6. Configure TLS Settings

- In the tunnel’s hostname configuration, open **TLS settings**.
- Enable **No TLS Verify** (turn it ON).

This setting disables strict certificate verification for backend services behind the tunnel.

---

## 7. Set Geo-based Security Rules (Optional)

- Go back to the normal Cloudflare dashboard for your domain.
- Navigate to **Security > WAF / Firewall Rules**.
- Create a rule to block traffic from outside the US, for example: 

Type: BLOCK: 

Rule: ```ip.src.country ne "US"```


This restricts access to only users originating from the US.

---

## 8. Special Rule for Audiobookshelf Android App

- Create a new firewall rule to target the Audiobookshelf app’s hostname, e.g.: ```(http.host eq "audiobookshelf.domain.com")```


- For this rule, **skip setting the “Security Level”** to avoid blocking or interfering with the app’s requests.

---

# Summary

By following these steps, you:

- Securely expose internal services via Cloudflare Tunnel.
- Protect your domain with Cloudflare’s Zero Trust security features.
- Control traffic based on geographic or hostname-based rules.

For further help, refer to the official [Cloudflare Tunnel documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/).

---