# Installation and use

## Current ChatGPT project or conversation

Attach the complete ZIP, or provide an accessible extracted skill folder. Add
`CHATGPT_PROJECT_INSTRUCTIONS.md` to the project's instructions, or attach it together
with the package. Explicitly ask the agent to read and use the skill. This makes the
workflow available as instructions in a file-capable conversation; it does not register
a globally installed skill or grant new tools. File and code-execution capabilities
must actually be available in that conversation.

Suggested first invocation:

> Use the Visual Asset Pipeline skill for this project. Inspect the current code and
> design rules, identify the visuals the interface needs, generate or recover the actual
> assets, install them in the correct project folders, integrate them into the code,
> and verify the result on desktop and mobile. Preserve the existing stack and local-CI
> workflow. Report any generation or file-transfer limitation rather than pretending a
> preview is already in the repository.

## Local skill-capable ChatGPT/Codex environments

Current OpenAI documentation lists repository `.agents/skills` and user
`$HOME/.agents/skills` locations. [R2]

For one repository, copy the entire `visual-asset-pipeline` directory to:

```text
<repo>/.agents/skills/visual-asset-pipeline/SKILL.md
```

For user-level use, use:

```text
<home>/.agents/skills/visual-asset-pipeline/SKILL.md
```

On Windows, `<home>` is the actual inspected user profile, not a guessed username.
Preserve other installed skills and any existing legacy skill directories. Do not
blindly replace an existing skill of this name. Use `$visual-asset-pipeline` or the
host's skill picker when supported. Reload/restart only if the host requires it.
No global installation has been performed merely by creating these files.

## Plugin-bundled skill

The separate plugin ZIP uses the portable plugin layout documented by OpenAI [R13]:

```text
visual-asset-pipeline-plugin/
  plugin.json
  skills/
    visual-asset-pipeline/
      SKILL.md
      ...
```

Use the host's documented local-plugin development/installation or organization
marketplace process. A ZIP is source packaging, not a promise that every ChatGPT
account has an arbitrary ZIP-upload installer. Once actually installed and exposed,
select the skill through the host's skill/plugin selector. Availability and workspace
policy must be checked in that host. This package intentionally declares no invented
MCP servers, credentials, connector IDs, or automatic paid services.

## Tools and optional dependencies

Native generation is preferred when it supports the required workflow. Access to that
tool is independent of skill installation. Inspect the live schema and output type.
An image-only turn boundary cannot be overridden by this skill.

Python helpers require Python 3.10+ and Pillow. Browser audit additionally needs
Playwright and a working Chromium installation. The optional paid API adapter needs
the OpenAI Python SDK, a server-side environment key, current model access, and explicit
separate billing authorization. Use approved environment/dependency installation
procedures; do not run global package installs just to activate the skill.

See `scripts/README.md` for commands and `RESEARCH.md` for the dated source register.
