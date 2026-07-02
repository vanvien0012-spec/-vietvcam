# Nginx + HTTPS deployment

This setup publishes VietVCam securely over HTTPS and proxies traffic to the local app at `127.0.0.1:8080`.

## 1) Install packages

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

## 2) Configure domain

Edit `deploy/nginx/vietvcam.conf` and replace:

- `vcam.example.com` with your real domain

Then install config:

```bash
sudo cp deploy/nginx/vietvcam.conf /etc/nginx/sites-available/vietvcam.conf
sudo ln -sf /etc/nginx/sites-available/vietvcam.conf /etc/nginx/sites-enabled/vietvcam.conf
sudo nginx -t
sudo systemctl reload nginx
```

## 3) Issue TLS certificate

```bash
sudo certbot --nginx -d vcam.example.com
```

Certbot sets automatic renew timer. Verify:

```bash
systemctl list-timers | grep certbot
```

## 4) Verify

```bash
curl https://vcam.example.com/health
```

Upload test:

```bash
curl -X POST "https://vcam.example.com/upload" \
  -H "x-upload-token: YOUR_TOKEN" \
  -F "file=@sample.mp4"
```
