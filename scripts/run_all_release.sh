#!/usr/bin/env bash

set -e

# this script runs the python script to trigger releases for multiple repositories
# it uses gh cli to authenticate and get the token

if ! gh auth status &> /dev/null; then
    gh auth login
fi

# disable shellcheck as this var is needed in the python script
# shellcheck disable=SC2155
export GH_TOKEN=$(gh auth token)

repos=(
    "NHSDigital/eps-prescription-tracker-ui"
    "NHSDigital/prescriptionsforpatients"
    "NHSDigital/eps-prescription-status-update-api"
    "NHSDigital/eps-FHIR-validator-lambda"
    "NHSDigital/eps-aws-vpc-resources"
    "NHSDigital/eps-aws-dashboards"
    "NHSDigital/electronic-prescription-service-clinical-prescription-tracker"
)

for repo in "${repos[@]}"; do
    read -r -p "Do you want to run the release for $repo? (y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        poetry run python3 scripts/trigger_release.py "$repo"
    fi
done
