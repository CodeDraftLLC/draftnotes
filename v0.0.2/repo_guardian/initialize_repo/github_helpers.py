import hmac
import hashlib
import logging


def verify_signature(payload, github_webhook_secret, signature):
    logging.info("Verifying webhook signature.")
    mac = hmac.new(
        github_webhook_secret.encode(), msg=payload, digestmod=hashlib.sha256
    )
    expected = "sha256=" + mac.hexdigest()
    result = hmac.compare_digest(expected, signature)
    logging.info(f"Signature verification result: {result}")
    return result


def get_team_of_user(github_client, github_org_name, username):
    logging.info(f"Getting team for user: {username} in org: {github_org_name}")
    org = github_client.get_organization(github_org_name)
    user_teams = []

    for team in org.get_teams():
        logging.debug(f"Checking team: {team.slug}")
        if any(member.login == username for member in team.get_members()):
            user_teams.append(team.slug)
            logging.debug(f"User {username} found in team: {team.slug}")

    if not user_teams:
        logging.warning(f"No team found for user: {username}")
        return None

    if len(user_teams) > 1:
        logging.warning(
            f"User {username} found in multiple teams: {user_teams}. Using first team: {user_teams[0]}"
        )
    else:
        logging.info(f"User {username} found in team: {user_teams[0]}")

    return user_teams[0]


def get_admin_team(github_client, github_org_name, team_slug):
    """Check if an admin version of the team exists and return its slug if found."""
    admin_team_slug = f"{team_slug}_Admin"
    logging.info(f"Checking if admin team exists: {admin_team_slug}")
    org = github_client.get_organization(github_org_name)
    try:
        admin_team = org.get_team_by_slug(admin_team_slug)
        logging.info(f"Admin team found: {admin_team_slug}")
        return admin_team_slug
    except Exception as e:
        logging.info(f"Admin team {admin_team_slug} not found: {e}")
        return None


def update_codeowners(repo, github_org_name, team_slug):
    logging.info(f"Updating CODEOWNERS file for team: {team_slug}")
    content = f"# CODEOWNERS\n*\t@{github_org_name}/{team_slug}\n"
    codeowners_path = ".github/CODEOWNERS"
    try:
        file = repo.get_contents(codeowners_path)
        repo.update_file(
            file.path,
            "🛡️ Guardian of Repos, First of His Name, "
            "Defender of Code updated CODEOWNERS for repo creator's team",
            content,
            file.sha,
        )
        logging.info("CODEOWNERS file updated.")
    except Exception as e:
        repo.create_file(
            codeowners_path, "Create CODEOWNERS for repo creator's team", content
        )
        logging.info("CODEOWNERS file created.")
        logging.debug(f"Exception: {e}")


def update_readme(repo, team_name):
    logging.info(f"Updating README.md for team: {team_name}")
    content = (
        "## 📦 Repository Ownership\n\n"
        f"**Team Responsible:** `{team_name}`  \n"
        "For issues or support, contact this team. Do not contact central platform team."
    )
    try:
        file = repo.get_contents("README.md")
        repo.update_file(
            file.path,
            "🛡️ Guardian of Repos, First of His Name, "
            "Defender of Code updated README.md for repo creator's team",
            content,
            file.sha,
        )
        logging.info("README.md updated.")
    except Exception as e:
        repo.create_file(
            "README.md", "Create README.md for repo creator's team", content
        )
        logging.info("README.md created.")
        logging.debug(f"Exception: {e}")


def assign_team_permissions(
    github_client,
    github_org_name,
    repo,
    team_slug,
    admin_team_slug=None,
    creator_username=None,
):
    logging.info(f"Assigning permissions for team: {team_slug}")
    org = github_client.get_organization(github_org_name)

    if admin_team_slug:
        # Assign write permissions to the regular team
        try:
            team = org.get_team_by_slug(team_slug)
            team.add_to_repos(repo)
            team.set_repo_permission(repo, "push")
            logging.info(f"Write permissions assigned to team: {team_slug}")
        except Exception as e:
            logging.error(
                f"Failed to assign write permissions to team {team_slug}: {e}"
            )

        # Assign admin permissions to the admin team
        try:
            admin_team = org.get_team_by_slug(admin_team_slug)
            admin_team.add_to_repos(repo)
            admin_team.set_repo_permission(repo, "admin")
            logging.info(f"Admin permissions assigned to admin team: {admin_team_slug}")
        except Exception as e:
            logging.error(
                f"Failed to assign admin permissions to admin team {admin_team_slug}: {e}"
            )
    else:
        # No admin team exists, assign admin permissions to regular team
        try:
            team = org.get_team_by_slug(team_slug)
            team.add_to_repos(repo)
            team.set_repo_permission(repo, "admin")
            logging.info(f"Admin permissions assigned to regular team: {team_slug}")
        except Exception as e:
            logging.error(
                f"Failed to assign admin permissions to team {team_slug}: {e}"
            )

    # Remove individual user permissions if creator_username is provided
    if creator_username:
        try:
            # Get the user object
            user = github_client.get_user(creator_username)
            # Remove the user as a collaborator (this removes direct permissions)
            repo.remove_from_collaborators(user)
            logging.info(
                f"Removed individual admin permissions from user: {creator_username}"
            )
        except Exception as e:
            # User might not have direct collaborator permissions, which is fine
            logging.debug(
                f"Could not remove collaborator permissions for {creator_username}: {e}"
            )
            logging.info(
                f"User {creator_username} permissions will be managed through team membership only"
            )
