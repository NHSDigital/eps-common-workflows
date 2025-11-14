# eps-common-workflows

A collection of common workflows used by other EPS repositories

The workflows that are available to use are

## combine dependabot prs

This workflow can be called to combine multiple open Dependabot PRs into a single PR.

#### Inputs

- `branchPrefix`: Branch prefix to find combinable PRs based on. Default: `dependabot`
- `mustBeGreen`: Only combine PRs that are green (status is success). Default: `true`
- `combineBranchName`: Name of the branch to combine PRs into. Default: `combine-dependabot-PRs`
- `ignoreLabel`: Exclude PRs with this label. Default: `nocombine`

#### Example

```yaml
name: Combine Dependabot PRs

on:
  workflow_dispatch:
    inputs:
      branchPrefix:
        description: "Branch prefix to find combinable PRs based on"
        required: true
        type: string
      mustBeGreen:
        description: "Only combine PRs that are green (status is success)"
        required: true
        type: boolean
      combineBranchName:
        description: "Name of the branch to combine PRs into"
        required: true
        type: string
      ignoreLabel:
        description: "Exclude PRs with this label"
        required: true
        type: string

jobs:
  combine-dependabot-prs:
    uses: NHSDigital/eps-common-workflows/.github/workflows/combine-dependabot-prs.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
    with:
      branchPrefix: ${{ github.event.inputs.branchPrefix }}
      mustBeGreen: ${{ github.event.inputs.mustBeGreen }}
      combineBranchName: ${{ github.event.inputs.combineBranchName }}
      ignoreLabel: ${{ github.event.inputs.ignoreLabel }}
```

## dependabot auto approve and merge
This workflow can be called to automatically approve and merge Dependabot PRs as part of the pull request workflow.

#### Requirements

Ensure that the `AUTOMERGE_APP_ID` and `AUTOMERGE_PEM` secrets are set, a `requires-manual-qa` PR label is created, and the repo is added to the `eps-autoapprove-dependabot` GitHub App.

#### Example

```yaml
name: Pull Request

on:
  pull_request:
    branches: [main]

jobs:
  dependabot-auto-approve-and-merge:
    uses: NHSDigital/eps-common-workflows/.github/workflows/dependabot-auto-approve-and-merge.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
    secrets:
      AUTOMERGE_APP_ID: ${{ secrets.AUTOMERGE_APP_ID }}
      AUTOMERGE_PEM: ${{ secrets.AUTOMERGE_PEM }}
```
## pr title check
This workflow checks that all pull requests have a title that matches the required format, and comments on the PR with a link to the relevant ticket if a ticket reference is found.

#### Example

To use this workflow in your repository, call it from another workflow file:

```yaml
name: Pull Request

on:
  pull_request:
    branches: [main]

jobs:
  pr_title_format_check:
    uses: NHSDigital/eps-common-workflows/.github/workflows/pr_title_check.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
```

## quality checks
This workflow runs common quality checks.   
To use this, you must have the following Makefile targets defined
- install
- check-licences
- lint
- test
- cdk-synth (only for cdk projects)

#### Inputs

- `install_java`: Whether to install java or not
- `run_sonar`: Whether to run sonar checks or not.
- `asdfVersion`: Override the version of asdf to install.
- `reinstall_poetry`: If you are using this from a primarily python based project, you should set this to true to force a poetry reinstallation after python is installed

#### Secret Inputs
- `SONAR_TOKEN`: Token used to authenticate to sonar

#### Outputs

None

#### Example

To use this workflow in your repository, call it from another workflow file:

```yaml
name: Release

on:
  workflow_dispatch:

jobs:
  quality_checks:
    uses: NHSDigital/eps-common-workflows/.github/workflows/quality-checks.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
    needs: [get_asdf_version]
    with:
      asdfVersion: ${{ needs.get_asdf_version.outputs.asdf_version }}
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```



## tag release
This workflow uses the semantic-release npm package to generate a new version tag, changelog, and github release for a repo.

#### Inputs

- `dry_run`: Whether to run in dry_run mode (do not create tags) or not
- `tagFormat`: Default `v\\${version}`. A template for the version tag.
- `branch_name`: The branch name to base the release on
- `publish_package`: Default false. If true, semantic-release will publish npm package.
- `asdfVersion`: Override the version of asdf to install.
- `main_branch`: The branch to use for publishing. Defaults to main

#### Outputs

- `version_tag`: The version tag created by semantic-release.
- `change_set_version`: A timestamped string that con be used for creating changesets.

#### Example

To use this workflow in your repository, call it from another workflow file:

```yaml
name: Release

on:
  workflow_dispatch:

jobs:
  tag_release:
    uses: NHSDigital/eps-common-workflows/.github/workflows/tag-release.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
  with:
    tagFormat: "v\\${version}-beta"
    dry_run: true
    asdfVersion: 0.18.0
    branch_name: main
    publish_package: false
```


## Secret scanning docker

The secret scanning also has a dockerfile, which can be run against a repo in order to scan it manually (or as part of pre-commit hooks). This can be done like so:
```bash
docker build -f https://raw.githubusercontent.com/NHSDigital/eps-workflow-quality-checks/refs/tags/v3.0.0/dockerfiles/nhsd-git-secrets.dockerfile -t git-secrets .
docker run -v /path/to/repo:/src git-secrets --scan-history .
```
For usage of the script, see the [source repo](https://github.com/NHSDigital/software-engineering-quality-framework/blob/main/tools/nhsd-git-secrets/git-secrets). Generally, you will either need `--scan -r .` or `--scan-history .`. The arguments default to `--scan -r .`, i.e. scanning the current state of the code.

In order to enable the pre-commit hook for secret scanning (to prevent developers from committing secrets in the first place), add the following to the `.devcontainer/devcontainer.json` file:
```json
{
    "remoteEnv": { "LOCAL_WORKSPACE_FOLDER": "${localWorkspaceFolder}" },
    "postAttachCommand": "docker build -f https://raw.githubusercontent.com/NHSDigital/eps-workflow-quality-checks/refs/tags/v4.0.2/dockerfiles/nhsd-git-secrets.dockerfile -t git-secrets . && pre-commit install --install-hooks -f",
    "features": {
      "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {
        "version": "latest",
        "moby": "true",
        "installDockerBuildx": "true"
      }
    }
}
```

And the this pre-commit hook to the `.pre-commit-config.yaml` file:
```yaml
repos:
- repo: local
  hooks:
    - id: git-secrets
      name: Git Secrets
      description: git-secrets scans commits, commit messages, and --no-ff merges to prevent adding secrets into your git repositories.
      entry: bash
      args:
        - -c
        - 'docker run -v "$LOCAL_WORKSPACE_FOLDER:/src" git-secrets --pre_commit_hook'
      language: system
```
