import os
import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from github import Github, GithubIntegration
from .github_helpers import (
    verify_signature,
    get_team_of_user,
    get_admin_team,
    update_codeowners,
    update_readme,
    assign_team_permissions,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("azure").setLevel(logging.WARNING)


# Setup Key Vault Client
key_vault_name = os.getenv("KEY_VAULT_NAME")
CPSUri = f"https://{key_vault_name}.vault.azure.net/"
credential = DefaultAzureCredential()
repoguardian_secret_client = SecretClient(vault_url=CPSUri, credential=credential)

github_app_id = repoguardian_secret_client.get_secret("RepoGuardianGHAppId").value
github_app_private_key = repoguardian_secret_client.get_secret(
    "RepoGuardianGHAppPrivateKey"
).value
github_webhook_secret = repoguardian_secret_client.get_secret(
    "RepoGuardianGHWebhookSecret"
).value
github_org_name = repoguardian_secret_client.get_secret("RepoGuardianGHOrgName").value


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing request to initialize repository guardian.")
    signature = req.headers.get("X-Hub-Signature-256")
    payload = req.get_body()
    if not signature or not verify_signature(payload, github_webhook_secret, signature):
        return func.HttpResponse("Invalid signature", status_code=401)

    event = req.headers.get("X-GitHub-Event")
    logging.info(f"Received event: {event}")
    data = req.get_json()

    if event == "repository" and data.get("action") == "created":
        repo_name = data["repository"]["name"]
        creator = data["sender"]["login"]

        integration = GithubIntegration(github_app_id, github_app_private_key)
        installation_id = data["installation"]["id"]
        access_token = integration.get_access_token(installation_id).token
        github_client = Github(access_token)

        repo = github_client.get_repo(f"{github_org_name}/{repo_name}")
        team_slug = get_team_of_user(github_client, github_org_name, creator)
        if not team_slug:
            return func.HttpResponse("Team not found for creator", status_code=400)

        # Check if admin team exists
        admin_team_slug = get_admin_team(github_client, github_org_name, team_slug)

        # Determine which team name to use for README
        team_name_for_readme = admin_team_slug if admin_team_slug else team_slug

        update_codeowners(repo, github_org_name, team_slug)
        update_readme(repo, team_name_for_readme)
        assign_team_permissions(
            github_client, github_org_name, repo, team_slug, admin_team_slug, creator
        )

        return func.HttpResponse("Processed", status_code=200)

    return func.HttpResponse("Ignored", status_code=200)
