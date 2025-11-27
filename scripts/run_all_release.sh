#!/usr/bin/env bash

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
    "NHSDigital/eps-vpc-resources"
    "NHSDigital/eps-aws-dashboards"
    "NHSDigital/electronic-prescription-service-clinical-prescription-tracker"
)

# Array to store repos that user wants to release
selected_repos=()

# Ask user for each repo
for repo in "${repos[@]}"; do
    read -r -p "Do you want to run the release for $repo? (y/n): " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        selected_repos+=("$repo")
    fi
done

# Check if any repos were selected
if [ ${#selected_repos[@]} -eq 0 ]; then
    echo "No repositories selected for release."
    exit 0
fi

echo ""
echo "Starting releases for ${#selected_repos[@]} repository(ies)..."
echo ""

# Array to store background process IDs
pids=()

# Launch releases in parallel
for repo in "${selected_repos[@]}"; do
    echo "Starting release for $repo..."
    poetry run python3 scripts/trigger_release.py "$repo" &
    pids+=($!)
done

echo ""
echo "All releases triggered. Waiting for completion..."
echo ""

# Wait for all background processes to complete and track their exit codes
failed_count=0
success_count=0

for pid in "${pids[@]}"; do
    if wait "$pid"; then
        ((success_count++))
    else
        ((failed_count++))
    fi
done

echo ""
echo "========================================"
echo "All releases completed!"
echo "Successful: $success_count"
echo "Failed: $failed_count"
echo "========================================"

# Exit with error if any releases failed
if [ $failed_count -gt 0 ]; then
    exit 1
fi

exit 0
