#!/usr/bin/env python3
"""
Script to trigger and monitor the GitHub release workflow.
Requires GH_TOKEN environment variable with permissions to trigger workflows.
"""

import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import requests


class GitHubWorkflowMonitor:
    """Monitor and control GitHub Actions workflow runs."""

    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.run_id: Optional[int] = None
        self.run_url: Optional[str] = None
        self.version_tag: Optional[str] = None
        self.jobs_requiring_approval = [
            "release_ref",
            "release_qa",
            "release_int"
        ]
        self.approved_jobs = set()
        self.completed_jobs = set()
        self.last_status_time = time.time()

    def trigger_workflow(
        self, workflow_file: str, branch: str = "main"
    ) -> bool:
        """Trigger the workflow dispatch event."""
        url = f"{self.base_url}/actions/workflows/{workflow_file}/dispatches"
        data = {
            "ref": branch
        }

        print(
            f"🚀 Triggering workflow '{workflow_file}' on branch '{branch}' "
            f"for repo '{self.owner}/{self.repo}'..."
        )
        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 204:
            print("✅ Workflow triggered successfully")
            return True
        else:
            print(f"❌ Failed to trigger workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    def get_latest_run(
        self, workflow_file: str, minutes: int = 2
    ) -> Optional[Dict[Any, Any]]:
        """Get the most recent workflow run started within the last N
        minutes."""
        url = f"{self.base_url}/actions/workflows/{workflow_file}/runs"
        params = {
            "per_page": 10,
            "status": "in_progress"
        }

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            print(f"❌ Failed to get workflow runs: {response.status_code}")
            return None

        data = response.json()
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        for run in data.get("workflow_runs", []):
            run_created = datetime.strptime(
                run["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)
            if run_created >= cutoff_time:
                return run

        return None

    def get_run_details(self, run_id: int) -> Optional[Dict[Any, Any]]:
        """Get details of a specific workflow run."""
        url = f"{self.base_url}/actions/runs/{run_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return None

    def get_run_jobs(self, run_id: int) -> Optional[Dict[Any, Any]]:
        """Get all jobs for a specific workflow run."""
        url = f"{self.base_url}/actions/runs/{run_id}/jobs"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return None

    def get_pending_deployments(self, run_id: int) -> Optional[list]:
        """Get pending deployment reviews for a workflow run."""
        url = f"{self.base_url}/actions/runs/{run_id}/pending_deployments"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return None

    def approve_deployment(self, run_id: int, environment_ids: list) -> bool:
        """Approve a pending deployment."""
        url = f"{self.base_url}/actions/runs/{run_id}/pending_deployments"
        data = {
            "environment_ids": environment_ids,
            "state": "approved",
            "comment": "Auto-approved by trigger_release.py script"
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            return True
        else:
            print(f"⚠️  Failed to approve deployment: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    def extract_version_tag(self, jobs_data: Dict[Any, Any]) -> Optional[str]:
        """Extract the version_tag output from the tag_release job."""
        for job in jobs_data.get("jobs", []):
            if job["name"] == "tag_release":
                # Check if job has completed successfully
                if job["conclusion"] == "success":
                    # Try to get outputs from the job
                    # (this may not be directly available)
                    # We'll need to check the run details
                    return self._get_job_outputs(job)
        return None

    def _get_job_outputs(self, job: Dict[Any, Any]) -> Optional[str]:
        """Try to extract outputs from job steps."""
        # GitHub API doesn't directly expose job outputs in the jobs endpoint
        # We need to parse from the run outputs or job logs
        # For now, we'll mark that we need to get this from the workflow
        # run outputs
        return None

    def get_workflow_outputs(self, run_id: int) -> Optional[Dict[str, Any]]:
        """Get workflow outputs (requires checking via runs endpoint)."""
        # GitHub doesn't expose workflow outputs directly via API
        # We'll need to infer from completed jobs or use alternate methods
        jobs_data = self.get_run_jobs(run_id)
        if not jobs_data:
            return None

        # Look for the tag_release job and check if we can find version info
        for job in jobs_data.get("jobs", []):
            if "tag_release" in job["name"].lower():
                if job["conclusion"] == "success":
                    # The version would be in the job outputs
                    # Since API doesn't expose this directly, we'll
                    # monitor job names that use the version (they
                    # receive it as input from tag_release)
                    return {"tag_release_completed": True}

        return None

    def check_for_errors(
        self, run_details: Dict[Any, Any], jobs_data: Dict[Any, Any]
    ) -> Optional[str]:
        """Check if any job has failed."""
        if run_details.get("conclusion") == "failure":
            return "Workflow run failed"

        for job in jobs_data.get("jobs", []):
            if job["conclusion"] == "failure":
                return f"Job '{job['name']}' failed"
            if job["conclusion"] == "cancelled":
                return f"Job '{job['name']}' was cancelled"

        return None

    def monitor_and_approve(self) -> bool:
        """Main monitoring loop."""
        print(f"\n📊 Monitoring workflow run: {self.run_url}\n")

        tag_release_completed = False

        while True:
            # Get current run details
            run_details = self.get_run_details(self.run_id)
            if not run_details:
                print("❌ Failed to get run details")
                return False

            jobs_data = self.get_run_jobs(self.run_id)
            if not jobs_data:
                print("❌ Failed to get jobs data")
                return False

            # Check for errors
            error = self.check_for_errors(run_details, jobs_data)
            if error:
                print(f"\n❌ ERROR: {error}")
                self.print_summary(error)
                return False

            # Track job statuses and detect changes
            current_job_status = {}
            for job in jobs_data.get("jobs", []):
                job_name = job["name"]
                job_status = job["status"]
                job_conclusion = job.get("conclusion")

                current_job_status[job_name] = (job_status, job_conclusion)

                # Detect newly completed jobs
                if (job_conclusion == "success" and
                        job_name not in self.completed_jobs):
                    self.completed_jobs.add(job_name)
                    print(f"✅ Job completed: {job_name}")

                    # Check if tag_release completed
                    if job_name == "tag_release / tag_release" and not tag_release_completed:
                        tag_release_completed = True
                        # Try to extract version from subsequent
                        # jobs that use it
                        self._extract_version_from_jobs(jobs_data)
                        if self.version_tag:
                            print(f"🏷️  Version tag: {self.version_tag}")

            # Check for pending deployments
            pending = self.get_pending_deployments(self.run_id)
            if pending:
                for deployment in pending:
                    env_name = deployment["environment"]["name"]
                    env_id = deployment["environment"]["id"]

                    # Check if this is release_prod
                    if env_name == "prod":
                        print(
                            f"\n🛑 Reached production deployment for "
                            f"environment '{env_name}'"
                        )
                        self.print_summary(
                            "Stopped at production deployment"
                        )
                        return True

                    # Auto-approve other environments
                    job_name = f"release_{env_name}"
                    if (job_name in self.jobs_requiring_approval and
                            job_name not in self.approved_jobs):
                        print(
                            f"✓ Approving deployment to environment "
                            f"'{env_name}'..."
                        )
                        if self.approve_deployment(self.run_id, [env_id]):
                            self.approved_jobs.add(job_name)
                            print(f"✅ Approved: {job_name}")
                        else:
                            print(f"⚠️  Failed to approve: {job_name}")

            # Check if workflow is complete
            if run_details.get("status") == "completed":
                if run_details.get("conclusion") == "success":
                    print("\n✅ Workflow completed successfully")
                    self.print_summary("Completed successfully")
                    return True
                else:
                    conclusion = run_details.get("conclusion", "unknown")
                    print(
                        f"\n⚠️  Workflow completed with conclusion: "
                        f"{conclusion}"
                    )
                    self.print_summary(
                        f"Completed with conclusion: {conclusion}"
                    )
                    return False

            # Print status update every 30 seconds
            current_time = time.time()
            if current_time - self.last_status_time >= 30:
                self.print_status_update(run_details, jobs_data)
                self.last_status_time = current_time

            # Sleep before next check
            time.sleep(10)

    def _extract_version_from_jobs(self, jobs_data: Dict[Any, Any]) -> None:
        """Try to extract version tag using GitHub CLI."""
        if self.version_tag:
            return  # Already have it

        try:
            import subprocess
            # Use gh CLI to get workflow run details with outputs
            result = subprocess.run(
                [
                    "gh", "run", "view", str(self.run_id),
                    "--repo", f"{self.owner}/{self.repo}",
                    "--json", "jobs"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                # Look through jobs for tag_release and
                # find jobs that depend on it
                for job in data.get("jobs", []):
                    # Look for jobs that use VERSION_NUMBER input
                    if "package_code" in job.get("name", ""):
                        # Try to extract from job name or check if
                        # we can get it from logs
                        # The version will be in the inputs but
                        # not directly available
                        pass

                # Try alternative: check recent tags
                tag_result = subprocess.run(
                    [
                        "gh", "api",
                        f"/repos/{self.owner}/{self.repo}/tags",
                        "--jq", ".[0].name"
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if tag_result.returncode == 0:
                    latest_tag = tag_result.stdout.strip()
                    if latest_tag:
                        self.version_tag = latest_tag

        except Exception:
            # If gh CLI fails, we'll just skip version extraction
            pass

    def print_status_update(
        self, run_details: Dict[Any, Any], jobs_data: Dict[Any, Any]
    ) -> None:
        """Print a status update."""
        status = run_details.get("status", "unknown")

        # Count jobs by status
        in_progress = sum(
            1 for j in jobs_data.get("jobs", [])
            if j["status"] == "in_progress"
        )
        completed = sum(
            1 for j in jobs_data.get("jobs", [])
            if j["status"] == "completed"
        )
        queued = sum(
            1 for j in jobs_data.get("jobs", [])
            if j["status"] == "queued"
        )

        print(
            f"⏳ Workflow still running... [Status: {status}, "
            f"Jobs: {completed} completed, {in_progress} in progress, "
            f"{queued} queued]"
        )

    def print_summary(self, outcome: str) -> None:
        """Print final summary."""
        print("\n" + "="*70)
        print(f"📋 RELEASE WORKFLOW SUMMARY {self.repo}")
        print("="*70)
        print(f"Workflow URL: {self.run_url}")
        print(f"Version Tag:  {self.version_tag or 'N/A'}")
        print(f"Outcome:      {outcome}")
        approved = ', '.join(sorted(self.approved_jobs)) or 'None'
        print(f"Approved:     {approved}")
        print("="*70 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Trigger and monitor GitHub release workflow'
    )
    parser.add_argument(
        'repo',
        help='Repository in format owner/repo '
             '(e.g., NHSDigital/eps-vpc-resources)'
    )
    parser.add_argument(
        '--workflow',
        default='release.yml',
        help='Workflow file name (default: release.yml)'
    )
    parser.add_argument(
        '--branch',
        default='main',
        help='Branch to trigger workflow on (default: main)'
    )

    args = parser.parse_args()

    # Parse repository
    try:
        owner, repo = args.repo.split('/')
    except ValueError:
        print(
            "❌ Error: Repository must be in format owner/repo "
            "(e.g., NHSDigital/eps-vpc-resources)"
        )
        sys.exit(1)

    # Get GitHub token
    token = os.environ.get("GH_TOKEN")
    if not token:
        print("❌ Error: GH_TOKEN environment variable not set")
        sys.exit(1)

    workflow_file = args.workflow
    branch = args.branch

    # Create monitor instance
    monitor = GitHubWorkflowMonitor(token, owner, repo)

    # Trigger the workflow
    if not monitor.trigger_workflow(workflow_file, branch):
        sys.exit(1)

    # Wait a moment for the run to be created
    print("⏳ Waiting for workflow run to start...")
    for attempt in range(12):  # Try for up to 2 minutes
        time.sleep(10)
        run = monitor.get_latest_run(workflow_file, minutes=3)
        if run:
            monitor.run_id = run["id"]
            monitor.run_url = run["html_url"]
            print(f"✅ Found workflow run: {monitor.run_url}")
            break

    if not monitor.run_id:
        print("❌ Failed to find the triggered workflow run")
        sys.exit(1)

    # Monitor and approve deployments
    success = monitor.monitor_and_approve()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
