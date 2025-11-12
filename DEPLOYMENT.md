# Deployment Guide

## Local Development

1. Make sure you have a `.env` file with the following variables:
```
# Azure OpenAI Configuration
ENDPOINT=your_endpoint
DEPLOYMENT=your_deployment
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_API_VERSION=2024-10-21

# User credentials (format: username1:password1,username2:password2)
APP_USERS=admin:admin123,hr_user:hrpass
```

2. Run the application:
```bash
streamlit run app.py
```

## Streamlit Cloud Deployment

### Option 1: Using Streamlit Secrets (Recommended)

1. Go to your app settings in Streamlit Cloud
2. Navigate to the "Secrets" section
3. Add the following secrets:

```toml
# Azure OpenAI Configuration
ENDPOINT = "your_endpoint"
DEPLOYMENT = "your_deployment"
AZURE_OPENAI_API_KEY = "your_api_key"
AZURE_OPENAI_API_VERSION = "2024-10-21"

# User credentials (format: username1:password1,username2:password2)
APP_USERS = "admin:admin123,hr_user:hrpass"
```

### Option 2: Using Environment Variables

In your Streamlit Cloud app settings, set these environment variables:
- `ENDPOINT`
- `DEPLOYMENT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `APP_USERS`

## Security Notes

- Never commit your `.env` file to version control
- Use strong passwords for your users
- Consider implementing password hashing for production
- In production, consider using a proper authentication system

## Adding/Modifying Users

To add or modify users, update the `APP_USERS` value:

**Format:** `username1:password1,username2:password2,username3:password3`

**Examples:**
- Single user: `admin:secretpassword`
- Multiple users: `admin:admin123,hr_user:hrpass,manager:manager456`

## Troubleshooting

### Credentials Not Loading
- Check that `APP_USERS` is set in either `.env` file or Streamlit secrets
- Verify the format is correct: `username:password,username2:password2`
- Make sure there are no extra spaces around usernames/passwords

### Azure OpenAI Not Working
- Verify all Azure OpenAI environment variables are set correctly
- Check that your API key is valid and not expired
- Ensure your deployment name matches the actual deployment in Azure