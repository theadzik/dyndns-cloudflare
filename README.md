# DynDNS-Cloudflare

DynDNS-Cloudflare is a simple dynamic dns client working with [cloudflare.com](https://www.cloudflare.com/).

****

## Getting started

### Prerequisites - Cloudflare

1. Follow the
   [account setup](https://developers.cloudflare.com/learning-paths/get-started/account-setup/create-account/)
   guide.

1. Create an
   [API Token](https://developers.cloudflare.com/learning-paths/get-started/account-setup/create-api-token/)
   with permissions to edit your zone DNS.

1. Add [your domain](https://developers.cloudflare.com/learning-paths/get-started/add-domain-to-cf/)

### Config

Depending on your environment provide environment variables either in
[docker-compose](docker-compose/docker-compose.yaml) or in [kubernetes](kubernetes-manifest/secret.yaml)

| Name                    | Description                                       | Required |
|-------------------------|---------------------------------------------------|----------|
| API_TOKEN               | Your Cloudflare API Token                         | Required |
| HOSTNAME                | Domain you would like to update, e.g. example.com | Required |
| LOG_LEVEL               | DEBUG, INFO or WARN                               | Optional |
| CHECK_ONLY_MODE         | Setting any value will disable updating DDNS      | Optional |
| SMTP_HOST               | SMTP server used to send warning emails           | Optional |
| SMTP_PORT               | SMTP port, defaults to 465                        | Optional |
| SMTP_USERNAME           | e.g. noreply@example.com                          | Optional |
| SMTP_PASSWORD           | Password to SMTP server                           | Optional |
| NOTIFICATION_EMAIL      | Address to receive warning emails                 | Optional |
| NOTIFICATION_ON_SUCCESS | Also send emails on successful DNS update         | Optional |

### Start DynDNS-Cloudflare

Start it with your container by running `docker-compose up`, `kubectl apply -k kubernetes-manifest`
or any other container runtime you use.
