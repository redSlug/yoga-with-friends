# yoga-with-friends - frontend
Simple user-facing website that renders the yoga enrollments retrieved from a bucket. Uses [vite](https://vite.dev/) and has hot reloading.

## Setup
### Configure Automatic Deploys
- created personal access token for the yoga-with-friends repo only w/ access to “actions / 
  deployments / pages / workflows / secrets”
- added it as a secrets / actions repository secret as 'G_ACCESS_TOKEN'
- selected build and deploy source "Github Actions"
- make sure ``VITE_YOGA_DATA_URL` has the right bucket location in [deploy.yaml](../.github/workflows/deploy.yaml)

### Troubleshooting / Security
Setup [some policies](../s3) for your bucket and [publisher](../s3/publisher_iam_permission_policy.json), and add an [index](../s3/index.html) file to your bucket
