from datetime import datetime
import requests
import sys

import pytz


class WorkflowData:
    def __init__(self, token, owner, repo, workflow, tz=""):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.workflow = workflow
        self.icon = "⚠"

        self.url = f"https://github.com/{owner}/{repo}/actions/workflows/{workflow}"
        print(self.url)

        # View API details:
        # https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-workflow
        request_url = (
            f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/runs"
        )
        payload = {}
        headers = {"accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
        response = requests.request("GET", request_url, headers=headers, data=payload)
        self.status_code = response.status_code

        if self.status_code == 200:  # success
            last_run = response.json()["workflow_runs"][0]
            self.conclusion = last_run["conclusion"]
            self.updated_at = last_run["updated_at"]
            if self.conclusion == "success":
                self.icon = "✓"
            if tz:
                utc_timestamp = datetime.strptime(self.updated_at, "%Y-%m-%dT%H:%M:%SZ")
                self.updated_at = utc_timestamp.astimezone(tz).strftime("%H:%M %b %d, %Y")

    def html_row(self):
        icon_color = 'class="red-icon"'
        if self.status_code == 200 and self.conclusion == "success":
            icon_color = 'class="green-icon"'

        if self.status_code == 200:
            return (
                f"<tr>"
                f"<td {icon_color}>{self.icon}</td>"
                f"<td>{self.repo}</td>"
                f'<td><a href="{self.url}">{self.workflow}</a></td>'
                f"<td>{self.conclusion}</td>"
                f"<td>{self.updated_at}</td>"
                f"</tr>"
            )
        else:
            return (
                f"<tr>"
                f"<td {icon_color}>{self.icon}</td>"
                f"<td>{self.repo}</td>"
                f'<td><a href="{self.url}">{self.workflow}</a></td>'
                f"<td>{self.status_code}</td>"
                f"<td></td>"
                f"</tr>"
            )

    def __str__(self):
        workflow_cell = self.workflow
        if self.url:
            workflow_cell = f"[{self.workflow}]({self.url})"
        if self.status_code == 200:
            return f"| {self.icon} | {self.repo} | {workflow_cell} | {self.conclusion} | {self.updated_at} |"
        else:
            return f"| {self.icon} | {self.repo} | {workflow_cell} | bad api call | --- |"


def update_readme(token, tz):
    file_name = "README.md"

    with open(file_name, "w") as file_out:

        def add_text(line):
            file_out.write(line)
            file_out.write("\n\n")

        def add_row(owner, repo, workflow):
            file_out.write(str(WorkflowData(token, owner, repo, workflow, tz=tz)))
            file_out.write("\n")

        add_text(f"Last Updated {datetime.now(tz).strftime('%H:%M %b %d, %y')}")

        file_out.write("| ? | repo | workflow | conclusion | updated at |\n")
        file_out.write("| - | ---- | -------- | ---------- | ---------- |\n")

        add_row("astronomy-commons", "lsdb", "smoke-test.yml")
        add_row("astronomy-commons", "lsdb", "testing-and-coverage.yml")
        add_row("astronomy-commons", "lsdb", "asv-nightly.yml")
        add_row("astronomy-commons", "lsdb", "build-documentation.yml")

        add_row("astronomy-commons", "hipscat", "smoke-test.yml")
        add_row("astronomy-commons", "hipscat", "testing-and-coverage.yml")
        add_row("astronomy-commons", "hipscat", "asv-nightly.yml")
        add_row("astronomy-commons", "hipscat", "build-documentation.yml")

        add_row("astronomy-commons", "hipscat-import", "smoke-test.yml")
        add_row("astronomy-commons", "hipscat-import", "testing-and-coverage.yml")
        add_row("astronomy-commons", "hipscat-import", "build-documentation.yml")

        add_row("lincc-frameworks", "tape", "build-documentation.yml")
        add_row("lincc-frameworks", "tape", "smoke-test.yml")
        add_row("lincc-frameworks", "tape", "testing-and-coverage.yml")


def update_html(token, tz):
    file_name = "index.html"

    with open(file_name, "w") as file_out:

        def add_text(line):
            file_out.write(line)
            file_out.write("\n\n")

        def add_row(owner, repo, workflow):
            file_out.write(WorkflowData(token, owner, repo, workflow, tz=tz).html_row())
            file_out.write("\n")

        # Write preamble
        html_preamble = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>LF Workflow Dashboard</title>
                <link rel="stylesheet" href="style.css">
            </head>
            <body>
            <table>
            <tr>
                <th> </th>
                <th>Repository</th>
                <th>Workflow</th>
                <th>Conclusion</th>
                <th>Last Run</th>
            </tr>
            """
        file_out.write(html_preamble)

        # Write middle

        # ASV Formatter
        add_row("lincc-frameworks", "asv-formatter", "smoke-test.yml")
        add_row("lincc-frameworks", "asv-formatter", "testing-and-coverage.yml")

        # Hipscat
        add_row("astronomy-commons", "hipscat", "smoke-test.yml")
        add_row("astronomy-commons", "hipscat", "testing-and-coverage.yml")
        add_row("astronomy-commons", "hipscat", "asv-nightly.yml")
        add_row("astronomy-commons", "hipscat", "build-documentation.yml")

        # Hipscat Import
        add_row("astronomy-commons", "hipscat-import", "smoke-test.yml")
        add_row("astronomy-commons", "hipscat-import", "testing-and-coverage.yml")
        add_row("astronomy-commons", "hipscat-import", "build-documentation.yml")

        # Koffi
        add_row("lincc-frameworks", "koffi", "smoke-test.yml")
        add_row("lincc-frameworks", "koffi", "testing-and-coverage.yml")

        # LSDB
        add_row("astronomy-commons", "lsdb", "smoke-test.yml")
        add_row("astronomy-commons", "lsdb", "testing-and-coverage.yml")
        add_row("astronomy-commons", "lsdb", "asv-nightly.yml")
        add_row("astronomy-commons", "lsdb", "build-documentation.yml")

        # PPT
        add_row("lincc-frameworks", "python-project-template", "ci.yml")

        # Rail
        add_row("lsstdesc", "rail", "build_documentation.yml")
        add_row("lsstdesc", "rail", "smoke-test.yml")
        add_row("lsstdesc", "rail", "testing-and-coverage.yml")
        add_row("lsstdesc", "rail_base", "smoke-test.yml")
        add_row("lsstdesc", "rail_base", "testing-and-coverage.yml")
        add_row("lsstdesc", "rail_pipelines", "main.yml")

        # Tables IO
        add_row("lsstdesc", "tables_io", "smoke-test.yml")
        add_row("lsstdesc", "tables_io", "testing-and-coverage.yml")

        # Tape
        add_row("lincc-frameworks", "tape", "build-documentation.yml")
        add_row("lincc-frameworks", "tape", "smoke-test.yml")
        add_row("lincc-frameworks", "tape", "testing-and-coverage.yml")

        # Write postamble
        file_out.write("</table>")
        file_out.write(f"<p>Last Updated {datetime.now(tz).strftime('%H:%M %b %d, %y')}</p>")
        file_out.write("</body></html>")


if __name__ == "__main__":
    token = sys.argv[1]
    tz = pytz.timezone("America/New_York")
    update_html(token, tz)
