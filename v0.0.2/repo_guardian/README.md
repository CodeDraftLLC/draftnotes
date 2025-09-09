# 🛡️ Repo Guardian

Repo Guardian is a GitHub App and automation toolkit designed to ensure every newly created repository starts with the right foundation.

## What Does It Do?

- **Automatic CODEOWNERS Update:**  
  Instantly updates the `CODEOWNERS` file to reflect the team of the repository creator, ensuring clear and accurate ownership.

- **README.md Ownership Injection:**  
  Adds or updates ownership information in the `README.md`, so everyone knows which team is responsible for the repo and where to direct support requests.

- **Seamless Team Tagging:**  
  Detects the creator’s team and tags the repository, assigning admin permissions to the correct team for streamlined management.

## Why Use Repo Guardian?

- **Promotes Clear Ownership:**  
  Every repo is tagged with the responsible team, reducing confusion and support overhead.

- **Consistent Engineering Standards:**  
  Ensures all repos start with best practices and compliance requirements.

## How It Works

**On Repository Creation:**  
   - Verifies the GitHub App secret.
   - Identifies the creator and their team.
   - Updates `CODEOWNERS` and `README.md` with team info.
   - Assigns admin permissions to the team.

## Example Ownership Section

```markdown
## 📦 Repository Ownership

**Team Responsible:** `<team-of-repo-creator>`  
**For issues or support, contact this team. Do not contact central platform team.`
```

---

Repo Guardian: First of Its Name, Defender of Code, Champion of Clarity.