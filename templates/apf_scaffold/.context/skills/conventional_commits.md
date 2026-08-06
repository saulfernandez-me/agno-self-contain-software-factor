# 📦 Skill: Conventional Commits & Pull Request Master

When synthesizing work for delivery, you must strictly follow the industry standard for semantic versioning and git history.

## 1. Commit Messages (The 5 Rules)
Every commit message must follow the Conventional Commits specification:
`<type>[optional scope]: <description>`

**Allowed Types:**
- `feat`: A new feature.
- `fix`: A bug fix.
- `docs`: Documentation only changes.
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `chore`: Changes to the build process or auxiliary tools and libraries.

**Rules:**
1. The description must be in lowercase.
2. No trailing period.
3. Use the imperative, present tense: "change" not "changed" nor "changes".

## 2. Pull Request Descriptions
Your PR description must be highly structured:
- Start with the title mirroring the main commit.
- Include a "Resolves #<Issue Number>" link.
- Provide a clear bulleted list of the exact technical changes made.
- Note any specific architectural decisions taken that deviate from standard practice.
