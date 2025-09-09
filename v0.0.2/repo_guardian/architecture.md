# Repo Guardian — Architecture

Repo Guardian is an Azure Function and GitHub App that enforces repository ownership and standards whenever a new repository.

---

## High-Level Architecture

```mermaid
flowchart LR
    Dev[Developer] -->|Creates repo| GH[(GitHub)]
    GH -->|Repository event webhook| AF[Azure Function: /initialize]
    AF -->|Verify HMAC Signature| AF
    AF -->|Fetch secrets| KV[(Azure Key Vault)]
    AF -->|Get installation token| GHA[(GitHub App)]
    AF -->|Update CODEOWNERS & README| GH
    AF -->|Assign team admin| GH
```

---

## Sequence: Repository Creation Event

```mermaid
sequenceDiagram
    autonumber
    participant D as Developer
    participant GH as GitHub
    participant AF as Azure Function (/initialize)
    participant KV as Azure Key Vault
    participant APP as GitHub App
    participant ORG as GitHub Org/Teams

    D->>GH: Create new repository
    GH->>AF: POST /initialize (repository event)
    AF->>AF: Verify X-Hub-Signature-256
    AF->>KV: Retrieve secrets
    AF->>APP: Get installation token
    AF->>GH: Get repo details
    AF->>ORG: Find creator's team
    AF->>GH: Update CODEOWNERS
    AF->>GH: Update README
    AF->>ORG: Assign team admin rights
```

