# eps-common-workflows

A collection of common workflows used by other EPS repositories

The workflows that are available to use are

## Workflow Index

- [Combine Dependabot PRs](#combine-dependabot-prs)
- [Dependabot Auto Approve and Merge](#dependabot-auto-approve-and-merge)
- [PR Title Check](#pr-title-check)
- [Get Repo Config](#get-repo-config)
- [Quality Checks](#quality-checks)
- [Quality Checks - Dev Container Version](#quality-checks---dev-container-version)
- [Tag Release](#tag-release)
- [Tag Release - Devcontainer Version](#tag-release---devcontainer-version)

## Other Docs

- [Adding Exclusions to Trivy Scanning](#adding-exclusions-to-trivy-scanning)
- [Secret Scanning Docker](#secret-scanning-docker)
- [Run All Releases](#run-all-releases)

## Adding Exclusions to Trivy Scanning
The quality checks job uses Trivy to scan for vulnerabilities.   
There may be times you want to add an exclusion for a known vulnerability that we are happy to accept
To do this, in the calling repo, add trivy.yaml with this content
```
ignorefile: ".trivyignore.yaml"
```
and add a .trivyignore.yaml with this content
```
vulnerabilities:
  - id: CVE-2026-24842
    paths:
      - "package-lock.json"
    statement: downstream dependency for tar - waiting for new npm release
    expired_at: 2026-06-01
```
See https://trivy.dev/docs/latest/configuration/filtering/#trivyignoreyaml for more details

## Combine Dependabot PRs

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

## Dependabot Auto Approve and Merge
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
## PR Title Check
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

## Get Repo Config

This workflow extracts common config values, including the devcontainer image and version. This image then has its attestations verified, and provides a pinned image reference that can be used in downstream workflows.

#### Inputs

- `registry`: Container registry host. Default: `ghcr.io`
- `namespace`: Image namespace/repository prefix. Default: `nhsdigital/eps-devcontainers`
- `owner`: GitHub owner used by `gh attestation verify --owner`. Default: `NHSDigital`
- `verify_published_from_main_image`: If true, verifies attestations published from `refs/heads/main`. Default: `true`
- `predicate_type`: Attestation predicate type. Default: `https://slsa.dev/provenance/v1`

#### Outputs

- `tag_format`: The tag format to use for releases.
- `devcontainer_image`: The pinned image reference for the devcontainer image.
- `devcontainer_version`: The version of the devcontainer image.
- `pinned_image`: The pinned image reference for the devcontainer image.
- `resolved_digest`: The resolved digest for the devcontainer image.

#### Example

To use this workflow in your repository, call it from another workflow file:

```yaml
name: Release

on:
  workflow_dispatch:

jobs:
  get_config_values:
    uses: NHSDigital/eps-common-workflows/.github/workflows/get-repo-config.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
```

## Quality Checks
This workflow runs common quality checks.   
To use this, you must have the following Makefile targets defined
- install
- lint
- test
- install-node (only for cdk projects)
- compile (only for cdk projects)
- cdk-synth (only for cdk projects)
- docker-build (only if run_docker_scan is set to true)

#### Inputs

- `install_java`: Whether to install Java or not
- `run_sonar`: Whether to run Sonar checks or not.
- `asdfVersion`: Override the version of asdf to install.
- `reinstall_poetry`: If you are using this from a primarily Python based project, you should set this to true to force a poetry reinstallation after Python is installed
- `run_docker_scan`: whether to run a scan of Docker images
- `docker_images`: csv list of Docker images to scan. These must match images produced by make docker-build

#### Secret Inputs
- `SONAR_TOKEN`: Token used to authenticate to Sonar

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

## Quality Checks - Dev Container Version
This workflow runs common quality checks using a prebuilt devcontainer (https://github.com/NHSDigital/eps-devcontainers).
To use this, you must have overridden any common makefile targets described in https://github.com/NHSDigital/eps-devcontainers?tab=readme-ov-file#common-makefile-targets
#### Inputs

- `run_sonar`: Whether to run Sonar checks or not.
- `run_docker_scan`: whether to run a scan of Docker images
- `docker_images`: csv list of Docker images to scan. These must match images produced by make docker-build
- `pinned_image`: A pinned, verified image version upon which to run the container.
#### Secret Inputs
- `SONAR_TOKEN`: Token used to authenticate to Sonar

#### Outputs

None

#### Example

To use this workflow in your repository, call it from another workflow file:

```yaml
name: Release

on:
  workflow_dispatch:

jobs:
  get_config_values:
    uses: NHSDigital/eps-common-workflows/.github/workflows/get-repo-config.yml@f5c8313a10855d0cc911db6a9cd666494c00045a

  quality_checks:
    uses: NHSDigital/eps-common-workflows/.github/workflows/quality-checks.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
    needs: [get_config_values]
    with:
      pinned_image: ${{ needs.get_config_values.outputs.pinned_image }}
      run_docker_scan: true
      docker_images: fhir-facade,validator
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## Tag Release
This workflow uses the semantic-release npm package to generate a new version tag, changelog, and GitHub release for a repo.

#### Inputs

- `dry_run`: Whether to run in dry_run mode (do not create tags) or not
- `tagFormat`: Default `v\\${version}`. A template for the version tag.
- `branch_name`: The branch name to base the release on
- `publish_package`: Default false. If true, semantic-release will publish npm package.
- `asdfVersion`: Override the version of asdf to install.
- `main_branch`: The branch to use for publishing. Defaults to main

#### Outputs

- `version_tag`: The version tag created by semantic-release.
- `change_set_version`: A timestamped string that can be used for creating changesets.

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

## Tag Release - Devcontainer Version
This workflow uses the semantic-release npm package to generate a new version tag, changelog, and GitHub release for a repo.   
*The devcontainer MUST have Node installed*
#### Inputs

- `dry_run`: Whether to run in dry_run mode (do not create tags) or not
- `branch_name`: The branch name to base the release on
- `pinned_image`: A pinned, verified image version upon which to run the container.
- `publish_packages`: comma separated list of package folders to publish to an npm registry
- `tagFormat`: Default `v\\${version}`. A template for the version tag.
- `main_branch`: The branch to use for publishing. Defaults to main
- `extra_artifact_name`: optional param to include an extra artifact in the release
- `extra_artifact_id`: optional param of the extra artifact id to include in the release
- `extra_artifact_run_id`: optional param of the run id to download the extra artifact id to include in the release
- `extra_artifact_repository` optional param to indicate which repo the run to download the artifact was from
- `verify_published_from_main_image` indicates if we should verify the image was published from main branch in eps-devcontainers

#### Outputs

- `version_tag`: The version tag created by semantic-release.
- `change_set_version`: A timestamped string that can be used for creating changesets.

#### Example

To use this workflow in your repository, call it from another workflow file:

```yaml
name: Release

on:
  workflow_dispatch:

jobs:
  get_config_values:
    uses: NHSDigital/eps-common-workflows/.github/workflows/get-repo-config.yml@f5c8313a10855d0cc911db6a9cd666494c00045a

  tag_release:
    uses: NHSDigital/eps-common-workflows/.github/workflows/tag-release-devcontainer.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
    needs: [get_config_values]
  with:
    tagFormat: "v\\${version}-beta"
    dry_run: true
    pinned_image: "${{ needs.get_config_values.outputs.pinned_image }}"
    branch_name: main
    publish_package: false
```


## Secret Scanning Docker

The secret scanning also has a Dockerfile, which can be run against a repo in order to scan it manually (or as part of pre-commit hooks). This can be done like so:
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

And add this pre-commit hook to the `.pre-commit-config.yaml` file:
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

## Run All Releases

There are some scripts that can be used to trigger releases for all our repos.   
It is invoked by running `./scripts/run_all_release.sh`.   
This first authenticates to GitHub using GitHub CLI tools to get a valid GitHub token.   

It then has an array of repos which it loops through asking for confirmation if you want to run deployment for it.   

For any that you have answered yes to, it then calls the Python script `scripts/trigger_release.py`.   

The Python script will trigger the release.yml workflow for that repo and monitor the run for it.   
When it reaches one of the steps release_qa, release_ref, release_int it will approve release to that environment.   
Once the run reaches release_prod step, the Python script will exit.   
The Python script will also exit if the GitHub run fails, or is cancelled at any step, or there is an unexpected response from GitHub (eg user does not have permission to approve a deployment).   
When the Python script finishes, it logs the run URL, the tag and summary of what happened.   
Python logs go to the console, and to a timestamped file in the logs folder.

When all runs of the python script have finished then the shell script exits showing a summary of failed and successful runs.   


If a run fails on a step BEFORE the tag_release step,  and the failure is transient (eg quality checks fails installing dependencies due to npm being down) then the whole release workflow can be rerun - either via this script or using the GitHub website.   

If a run fails on a step AFTER the tag_release step, and the failure is transient (eg regression tests failure) then that failing step can just be re-run manually via the GitHub website.   

If a run fails due to a code or cloudformation/cdk issue, then a new pull request should be created to fix this, merged to main, and a new release triggered.   
