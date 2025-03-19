
# Frontend

## Configure Automatic Deploys
- created personal access token for the yoga-with-friends repo only w/ access to “actions / 
  deployments / pages / workflows / secrets”
- added it as a secrets / actions repository secret as 'G_ACCESS_TOKEN'
- selected build and deploy source "Github Actions"

## Troubleshooting / Security
- make sure the CORS policy on the `yoga.json` resource allows access from the frontend, for example:
```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET"
        ],
        "AllowedOrigins": [
            "http://localhost:5173",
            "https://yourdomain.com",
            "https://redslug.github.io"
        ],
        "ExposeHeaders": []
    }
]
```
