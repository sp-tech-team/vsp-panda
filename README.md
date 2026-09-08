# vsp-panda
This repository is used for the new code of Volunteer Support Portal.

## Browser tests in GitHub Actions

The workflow at `.github/workflows/python-tests.yml` runs the Playwright tests in
`test_automation/tests` on pushes and pull requests targeting `main`. It can
also be started manually from the repository's **Actions** tab using
**Run workflow**.

The tests use the following URL, in order:

1. The manual `base_url` input.
2. The repository variable `VSP_BASE_URL`.
3. `https://vsp-panda.streamlit.app/`.

Set `VSP_BASE_URL` to a staging deployment before enabling push or pull-request
runs. These scenarios submit requests and should not normally run against a
production database.

## Run browser tests locally

From PowerShell, install the test dependencies and Chromium once:

```powershell
python -m pip install -r test_automation/requirements-test.txt
python -m playwright install chromium
```

Run the complete suite against the default deployed URL:

```powershell
./run-tests.ps1
```

Run against another deployment or run only one suite:

```powershell
./run-tests.ps1 -BaseUrl "https://your-staging-url/" -TestPath "tests/initialformtests.py"
```

You can also run directly from `test_automation`:

```powershell
cd test_automation
$env:BASE_URL = "https://your-staging-url/"
python -m pytest -v
```

Local runs open a visible browser. GitHub Actions sets `CI=true` and runs
Chromium headlessly.
