#!/usr/bin/env python3

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, TextArea
from textual.containers import Vertical, Horizontal
import subprocess
import os
import sys
import importlib

# ===================== PATH =====================
BASE_DIR = os.path.expanduser("~/lmpui")
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
RESULT_DIR = os.path.join(BASE_DIR, "result")
ANALYSIS_DIR = os.path.join(BASE_DIR, "analisis")
SUBMIT_DIR = os.path.join(BASE_DIR, "submit")
LMP_PROG = os.path.expanduser("/opt/bin/lmp_mpi")

sys.path.append(ANALYSIS_DIR)

# ===================== UTIL =====================
def run_shell(cmd: str) -> str:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=BASE_DIR)
    return r.stdout.strip() or r.stderr.strip()

def run_sbatch(stage: str, input_file: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    template = os.path.join(SUBMIT_DIR, "submit.bash")
    generated = os.path.join(SUBMIT_DIR, "submit_generated.bash")

    if not os.path.exists(template):
        return "submit not found."

    with open(template) as f:
        txt = f.read()
        
    jobname = os.path.splitext(os.path.basename(input_file))[0]

    txt = (
        txt.replace("JOBNAME", jobname)
           .replace("NTASKS", "2")
           .replace("LMP_PROG", LMP_PROG)
           .replace("INPUT_FILE", input_file)
    )

    with open(generated, "w") as f:
        f.write(txt)

    return run_shell(f"sbatch {generated}")

def get_user_jobs():
    output = run_shell("squeue -u $USER -h -o '%i %j'")
    jobs = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            jobs.append((parts[0], parts[1]))
    return jobs

# ===================== MAIN MENU =====================
class MainMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Button("FILES", id="files"),
            Button("RELAX", id="relax"),
            Button("JOIN", id="join"),
            Button("HEATHOLD", id="heathold"),
            Button("STATISTICS", id="statistics"),
            Button("RESULT", id="result"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "statistics":
            import STATS_ANALYSIS
            importlib.reload(STATS_ANALYSIS)
            msd_dir = os.path.join(OUTPUT_DIR, "msd")
            result_dir = os.path.join(RESULT_DIR, "statistics")
            os.makedirs(result_dir, exist_ok=True)
            STATS_ANALYSIS.run_statistics(msd_dir, result_dir)

            self.app.notify("Statistical analysis completed.")

        else:
            self.app.push_screen({
                "files": FileMenu(),
                "relax": StageMenu("relax"),
                "join": StageMenu("join"),
                "heathold": StageMenu("heathold"),
                "result": ResultStageMenu(),
        }[e.button.id])

# ===================== FILE MENU (STAGE LEVEL) =====================
class FileMenu(Screen):
    def compose(self):
        yield Header()
        yield Vertical(
            Button("RELAX FILES", id="relax"),
            Button("JOIN FILES", id="join"),
            Button("HEATHOLD FILES", id="heathold"),
            Button("BACK", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        else:
            self.app.push_screen(StageFileMenu(e.button.id))

# ===================== STAGE FILE MENU =====================
class StageFileMenu(Screen):
    def __init__(self, stage):
        super().__init__()
        self.stage = stage
        self.stage_dir = os.path.join(INPUT_DIR, stage)
        os.makedirs(self.stage_dir, exist_ok=True)

    def compose(self):
        yield Header()
        yield Static(f"{self.stage.upper()} FILE MANAGEMENT")
        yield Vertical(
            Button("NEW FILE", id="new"),
            Button("OPEN FILES", id="open"),
            Button("REMOVE FILES", id="remove"),
            Button("BACK", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "new":
            self.app.push_screen(NewStageFile(self.stage))
        elif e.button.id == "open":
            self.app.push_screen(FileBrowser(self.stage_dir))
        elif e.button.id == "remove":
            self.app.push_screen(RemoveFileBrowser(self.stage_dir))
        elif e.button.id == "back":
            self.app.pop_screen()

# ===================== NEW FILE =====================
class NewStageFile(Screen):
    def __init__(self, stage):
        super().__init__()
        self.stage = stage
        self.stage_dir = os.path.join(INPUT_DIR, stage)

    def compose(self):
        yield Header()
        yield Static("Nano will open.\nSave Ctrl+O → Exit Ctrl+X")
        yield Button("START", id="start")
        yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "start":
            filepath = os.path.join(self.stage_dir, "newfile.in")
            with self.app.suspend():
                subprocess.run(["nano", filepath])
            self.app.pop_screen()
        elif e.button.id == "back":
            self.app.pop_screen()

# ===================== FILE BROWSER =====================
class FileBrowser(Screen):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.file_map = {}

    def compose(self):
        yield Header()
        yield Static(f"Directory: {self.directory}")
        with Vertical():
            if os.path.exists(self.directory):
                for i, f in enumerate(sorted(os.listdir(self.directory))):
                    if f.startswith(".") or f.endswith(".swp"):
                        continue
                    path = os.path.join(self.directory, f)
                    if os.path.isfile(path):
                        self.file_map[f"f_{i}"] = path
                        yield Button(f, id=f"f_{i}")
            yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id in self.file_map:
            self.app.push_screen(FileView(self.file_map[e.button.id]))

# ===================== REMOVE FILE =====================
class RemoveFileBrowser(Screen):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.file_map = {}

    def compose(self):
        yield Header()
        yield Static("REMOVE FILES")
        with Vertical():
            if os.path.exists(self.directory):
                for i, f in enumerate(sorted(os.listdir(self.directory))):
                    if f.startswith(".") or f.endswith(".swp"):
                        continue
                    path = os.path.join(self.directory, f)
                    if os.path.isfile(path):
                        self.file_map[f"r_{i}"] = path
                        yield Button(f, id=f"r_{i}")
            yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id in self.file_map:
            os.remove(self.file_map[e.button.id])
            self.app.pop_screen()

# ===================== FILE VIEW =====================
class FileView(Screen):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.is_output = filepath.startswith(RESULT_DIR)

    def compose(self):
        yield Header()
        with Horizontal():
            with Vertical():
                yield Static(f"FILE:\n{self.filepath}")
                if not self.is_output:
                    yield Button("EDIT", id="edit")
                yield Button("BACK", id="back")
            with Vertical():
                try:
                    with open(self.filepath, encoding="utf-8") as f:
                        content = f.read()
                except:
                    content = "[BINARY / IMAGE FILE]"
                yield TextArea(content, read_only=True)
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id == "edit":
            with self.app.suspend():
                subprocess.run(["vim", self.filepath])

# ===================== STAGE MENU =====================
class StageMenu(Screen):
    def __init__(self, stage):
        super().__init__()
        self.stage = stage

    def compose(self):
        s = self.stage.upper()
        yield Header()
        yield Vertical(
            Button(f"RUN {s}", id="run"),
            Button(f"SQUEUE {s}", id="queue"),
            Button(f"ANALYSIS {s}", id="analysis"),
            Button(f"CANCEL {s}", id="cancel"),
            Button("BACK", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "run":
            self.app.push_screen(StageInputSelector(self.stage))
        elif e.button.id == "queue":
            self.app.push_screen(QueueScreen())
        elif e.button.id == "cancel":
            self.app.push_screen(CancelJobSelector())
        elif e.button.id == "analysis":
            stage_dir = os.path.join(RESULT_DIR, self.stage)
            os.makedirs(stage_dir, exist_ok=True)
            if self.stage == "relax":
                import RELAX_ANALYSIS
                importlib.reload(RELAX_ANALYSIS)
                RELAX_ANALYSIS.main(stage_dir)
            elif self.stage == "join":
                import JOIN_ANALYSIS
                importlib.reload(JOIN_ANALYSIS)
                JOIN_ANALYSIS.main(stage_dir)
            elif self.stage == "heathold":
                import HEATHOLD_ANALYSIS
                importlib.reload(HEATHOLD_ANALYSIS)
                HEATHOLD_ANALYSIS.main(stage_dir)
            self.app.notify(f"ANALYSIS {self.stage.upper()} SAVED.")
        elif e.button.id == "back":
            self.app.pop_screen()

# ===================== INPUT SELECTOR =====================
class StageInputSelector(Screen):
    def __init__(self, stage):
        super().__init__()
        self.stage = stage
        self.stage_input_dir = os.path.join(INPUT_DIR, stage)
        self.file_map = {}

    def compose(self):
        yield Header()
        yield Static(f"Select {self.stage.upper()} input file")
        with Vertical():
            if os.path.exists(self.stage_input_dir):
                for i, f in enumerate(sorted(os.listdir(self.stage_input_dir))):
                    if f.endswith(".in"):
                        path = os.path.join(self.stage_input_dir, f)
                        self.file_map[f"id_{i}"] = path
                        yield Button(f, id=f"id_{i}")
            yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id in self.file_map:
            result = run_sbatch(self.stage, self.file_map[e.button.id])
            self.app.pop_screen()
            self.app.notify(result)

# ===================== CANCEL SELECTOR =====================
class CancelJobSelector(Screen):
    def compose(self):
        yield Header()
        yield Static("Select Job to Cancel")
        self.jobs = get_user_jobs()
        with Vertical():
            if not self.jobs:
                yield Static("No running jobs.")
            else:
                for i, (jobid, jobname) in enumerate(self.jobs):
                    yield Button(f"{jobid} | {jobname}", id=f"job_{i}")
            yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id.startswith("job_"):
            idx = int(e.button.id.split("_")[1])
            jobid, _ = self.jobs[idx]
            run_shell(f"scancel {jobid}")
            self.app.pop_screen()
            self.app.notify(f"Canceled batch job {jobid}")

# ===================== QUEUE =====================
class QueueScreen(Screen):
    def compose(self):
        yield Header()
        yield TextArea(run_shell("squeue -u $USER"), read_only=True)
        yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()

# ===================== RESULT =====================
class ResultStageMenu(Screen):
    def compose(self):
        yield Header()
        yield Vertical(
            Button("RELAX RESULT", id="relax"),
            Button("JOIN RESULT", id="join"),
            Button("HEATHOLD RESULT", id="heathold"),
            Button("STATISTICS RESULT", id="statistics"),
            Button("BACK", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        else:
            self.app.push_screen(FileBrowser(os.path.join(RESULT_DIR, e.button.id)))

# ===================== APP =====================
class LammpsUI(App):
    CSS = """
    Vertical { align: center middle; }
    Button { width: 42; margin: 1; }
    """

    def on_mount(self):
        self.push_screen(MainMenu())

if __name__ == "__main__":
    LammpsUI().run()
