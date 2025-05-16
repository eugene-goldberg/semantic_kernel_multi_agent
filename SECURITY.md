# Security Best Practices

## Handling Sensitive Information

This document provides guidance on securely handling sensitive information like API keys, secrets, and credentials when working with this project.

### Environment Variables

#### Local Development

1. **Create a Local `.env` File**:
   ```bash
   cp .env.sample .env
   ```

2. **Add Your Credentials**:
   Edit the `.env` file with your actual credentials:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-actual-api-key
   ...
   ```

3. **IMPORTANT: Never Commit Credentials**:
   - The `.gitignore` file is set up to exclude `.env` and `.env.*` files (except `.env.sample`)
   - Double-check that you haven't staged any files containing credentials before committing
   - Run `git diff --staged` to verify no credentials are being committed

#### GitHub Secrets for CI/CD

For GitHub Actions or other CI/CD pipelines, use repository secrets:

1. Navigate to your repository on GitHub
2. Go to Settings > Secrets and variables > Actions
3. Add secrets for all required variables:
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - etc.

4. Reference these secrets in your workflow YAML files:
   ```yaml
   env:
     AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
     AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
   ```

#### Azure Key Vault (Production)

For production deployments, consider using Azure Key Vault:

1. Store all secrets in Azure Key Vault
2. Use managed identities to access the secrets
3. Configure your application to retrieve secrets at runtime

### Service Principals

If you're using Azure Service Principals:

1. Create a service principal with minimal required permissions
2. Store the credentials securely in your environment variables or Key Vault
3. Regularly rotate the client secret
4. Consider using certificate-based authentication instead of client secrets

### Credential Rotation

Regularly rotate your credentials:

1. Azure OpenAI API keys: Every 30-90 days
2. Service Principal secrets: Every 30-60 days
3. After any team member with access leaves the project

### What to Do If Credentials Are Exposed

If you accidentally commit or push credentials:

1. **Immediately Revoke/Rotate the Credentials**:
   - For Azure OpenAI: Regenerate the API key
   - For Service Principals: Create a new client secret and delete the old one

2. **Remove the Credentials from Git History**:
   - Use the BFG Repo-Cleaner: https://rtyley.github.io/bfg-repo-cleaner/
   - Or Git Filter-Branch (for advanced users)

3. **Force Push the Cleaned History**:
   ```bash
   git push --force
   ```

4. **Notify Relevant Stakeholders**

### Secure Deployment

For secure deployments:

1. Use environment-specific configuration files (dev, staging, prod)
2. Load the appropriate environment variables based on the deployment environment
3. Ensure deployment scripts don't log or expose credentials
4. Verify that logs don't contain sensitive information

## Additional Resources

- [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Microsoft Security Best Practices](https://docs.microsoft.com/en-us/azure/security/fundamentals/identity-management-best-practices)