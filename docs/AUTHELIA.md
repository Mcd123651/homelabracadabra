# Authelia Bootstrap Users and SMTP Setup

This setup includes a default `users_database.yml` for bootstrapping Authelia with basic access. **The default password is `123456` – please change it immediately.**
[SWAG Guide](https://www.authelia.com/integration/proxies/swag/)


## Generate Password Hashes

To generate a secure password hash using Argon2id:

```bash
docker run --rm authelia/authelia:latest authelia crypto hash generate --password 123456
```

### Gmail SMTP Example
```bash
notifier:
  smtp:
    username: <email address>
    password: <gmail app password>  # Not your Gmail password – see below!
    address: smtp.gmail.com:587
    sender: <email address>
    subject: "[Authelia] {title}"
    startup_check_address: <email address>
    identifier: gmail.com
    tls:
      server_name: smtp.gmail.com
      skip_verify: false
    disable_require_tls: false
    disable_starttls: false
```

### OIDC Setup Example:

generate secure secrets:
```bash
openssl rand -hex 32
```
Generate an RSA private key for signing tokens:
```bash
openssl genrsa -out oidc.key 2048
```
add to configuration.yml:
```yaml
identity_providers:
  oidc:
    hmac_secret: '3f53....'
    jwks:
      - key_id: 'example'
        algorithm: 'RS256'
        use: 'sig'
        key: |
          -----BEGIN PRIVATE KEY-----

          -----END PRIVATE KEY-----
    clients:
      - client_id: audiobookshelf
        client_name: "Audiobookshelf"
        client_secret: "e4a7...."
        redirect_uris:
          - "https://audiobookshelf.domain.com/audiobookshelf/auth/openid/callback"
          - "https://audiobookshelf.domain.com/audiobookshelf/auth/openid/mobile-redirect"
        scopes:
          - openid
          - profile
          - email
          - groups
        grant_types:
          - authorization_code
        response_types:
          - code
        token_endpoint_auth_method: client_secret_basic
    enable_client_debug_messages: true  # Optional, for debugging
```