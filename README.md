# eps-common-workflows

A collection of common workflows used by other EPS repositories

The workflows that are available to use are

## Workflow Index

- [Dependabot Auto Approve and Merge](#dependabot-auto-approve-and-merge)
- [PR Title Check](#pr-title-check)
- [Get Repo Config](#get-repo-config)
- [Quality Checks - Dev Container Version](#quality-checks---dev-container-version)
- [Tag Release - Devcontainer Version](#tag-release---devcontainer-version)

## Other Docs

- [Run All Releases](#run-all-releases)


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
- `devcontainer_image`: The devcontainer image name as defined in `.devcontainer/devcontainer.json`.
- `devcontainer_version`: The version of the devcontainer image.
- `pinned_image`: The fully-qualified digest-pinned image reference.
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
    uses: NHSDigital/eps-common-workflows/.github/workflows/quality-checks-devcontainer.yml@f5c8313a10855d0cc911db6a9cd666494c00045a
    needs: [get_config_values]
    with:
      pinned_image: ${{ needs.get_config_values.outputs.pinned_image }}
      run_docker_scan: true
      docker_images: fhir-facade,validator
    secrets:
      SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

## Tag Release - Devcontainer Version
This workflow uses the semantic-release npm package to generate a new version tag, changelog, and GitHub release for a repo.   
*The devcontainer MUST have Node installed*
#### Inputs

- `dry_run`: Whether to run in dry_run mode (do not create tags) or not
- `branch_name`: The branch name to base the release on
- `pinned_image`: A pinned, verified image version upon which to run the container.
- `publish_packages`: comma separated list of package folders to publish to an npm registry
- `tag_format`: Default `v\\${version}`. A template for the version tag.
- `main_branch`: The branch to use for publishing. Defaults to main
- `extra_artifact_name`: optional param to include an extra artifact in the release
- `extra_artifact_id`: optional param of the extra artifact id to include in the release
- `extra_artifact_run_id`: optional param of the run id to download the extra artifact id to include in the release
- `extra_artifact_repository`: optional param to indicate which repo the run to download the artifact was from

#### Outputs

- `version_tag`: The version tag created by semantic-release.
- `change_set_version`: A timestamped string that can be used for creating changesets.
- `next_version_tag`: The next version tag that will be created.

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
      tag_format: "v\\${version}-beta"
      dry_run: true
      pinned_image: "${{ needs.get_config_values.outputs.pinned_image }}"
      branch_name: main
      publish_packages: ""
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
