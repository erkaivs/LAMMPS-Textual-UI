#!/usr/bin/env python3

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, TextArea
from textual.containers import Vertical, Horizontal
import subprocess
import os
import sys
import importlib
import shutil

# ===================== PATH =====================

def get_paths(app):
    if not app.current_sim:
        raise RuntimeError("No simulation selected")

    root = os.path.expanduser("~/lmpui")
    base = os.path.join(root, app.current_sim)

    return {
        "root": root,
        "base": base,
        "input": os.path.join(base, "input"),
        "output": os.path.join(base, "output"),
        "result": os.path.join(base, "result"),
        "analysis": os.path.join(base, "analIsis"),
        "submit": os.path.join(base, "submit")
    }

LMP_PROG = os.path.abspath("/opt/bin/lmp_mpi")

# ===================== UTIL =====================

def run_shell(cmd: str, app) -> str:
    paths = get_paths(app)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=paths["base"])
    return r.stdout.strip() or r.stderr.strip()

def run_sbatch(stage: str, input_file: str, app) -> str:
    paths = get_paths(app)

    os.makedirs(paths["output"], exist_ok=True)
    os.makedirs(paths["submit"], exist_ok=True)

    template = os.path.join(paths["submit"], "submit.bash")
    generated = os.path.join(paths["submit"], "submit_generated.bash")

    # DEBUG
    if not os.path.exists(template):
        return f"ERROR: submit.bash not found at {template}"

    with open(template) as f:
        txt = f.read()

    jobname = os.path.splitext(os.path.basename(input_file))[0]

    input_file = os.path.abspath(input_file)

    txt = (
        txt.replace("JOBNAME", jobname)
           .replace("NTASKS", "2")
           .replace("LMP_PROG", LMP_PROG)
           .replace("INPUT_FILE", input_file)
    )

    with open(generated, "w") as f:
        f.write(txt)

    return run_shell(f"sbatch {generated}", app)

def get_user_jobs(app):
    output = run_shell("squeue -u $USER -h -o '%i %j'", app)
    jobs = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            jobs.append((parts[0], parts[1]))
    return jobs

# ===================== SIMULATION =====================

def list_sims(app):
    root = os.path.expanduser("~/lmpui")
    if not os.path.exists(root):
        return []
    return sorted([
        d for d in os.listdir(root)
        if d.startswith("sim") and os.path.isdir(os.path.join(root, d))
    ])

def next_sim_name(root):
    i = 1
    while True:
        name = f"sim{i}"
        if not os.path.exists(os.path.join(root, name)):
            return name
        i += 1

def create_sim(app):
    root = os.path.expanduser("~/lmpui")
    src = os.path.join(root, "lmpui_template")

    if not os.path.exists(src):
        return None

    name = next_sim_name(root)
    dst = os.path.join(root, name)

    shutil.copytree(src, dst)
    return name

# ===================== MAIN MENU =====================

class MainMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Button("SIMULATIONS", id="sim"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "sim":
            self.app.push_screen(SimulationMenu())

# ===================== SIM MENU =====================

class SimulationMenu(Screen):
    def compose(self):
        yield Header()
        yield Vertical(
            Button("OPEN SIMULATION", id="open"),
            Button("NEW SIMULATION", id="new"),
            Button("BACK", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "open":
            self.app.push_screen(SimSelect())

        elif e.button.id == "new":
            sim_name = create_sim(self.app)
            if sim_name:
                self.app.current_sim = sim_name
                self.app.notify(f"created {sim_name}")
                self.app.push_screen(SimulationDashboard())
            else:
                self.app.notify("template missing")

        elif e.button.id == "back":
            self.app.pop_screen()

# ===================== SIM SELECT =====================

class SimSelect(Screen):
    def compose(self):
        yield Header()
        sims = list_sims(self.app)

        with Vertical():
            if not sims:
                yield Static("NO SIMULATIONS")

            for i, s in enumerate(sims):
                yield Button(s, id=f"s_{i}")

            yield Button("BACK", id="back")

        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()

        elif e.button.id.startswith("s_"):
            idx = int(e.button.id.split("_")[1])
            sim = list_sims(self.app)[idx]

            self.app.current_sim = sim
            self.app.push_screen(SimulationDashboard())

# ===================== DASHBOARD =====================

class SimulationDashboard(Screen):
    def compose(self):
        yield Header()
        yield Static(f"SIM: {self.app.current_sim}")

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
            paths = get_paths(self.app)

            sys.path.append(paths["analysis"])
            import STATS_ANALYSIS
            importlib.reload(STATS_ANALYSIS)

            msd_dir = os.path.join(paths["output"], "msd")
            result_dir = os.path.join(paths["result"], "statistics")
            os.makedirs(result_dir, exist_ok=True)

            STATS_ANALYSIS.run_statistics(msd_dir, result_dir)

        else:
            self.app.push_screen({
                "files": FileMenu(),
                "relax": StageMenu("relax"),
                "join": StageMenu("join"),
                "heathold": StageMenu("heathold"),
                "result": ResultStageMenu(),
            }[e.button.id])

# ===================== FILE MENU =====================

class FileMenu(Screen):
    def compose(self):
        yield Header()
        yield Vertical(
            Button("RELAX FILES", id="relax"),
            Button("JOIN FILES", id="join"),
            Button("HEATHOLD FILES", id="heathold"),
            Button("BACK", id="back"),
            Button("BACK TO SIMS", id="root"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id == "root":
            self.app.current_sim = None
            self.app.switch_screen(MainMenu())
        else:
            self.app.push_screen(StageFileMenu(e.button.id))

# ===================== STAGE FILE =====================

class StageFileMenu(Screen):
    def __init__(self, stage):
        super().__init__()
        self.stage = stage

    def compose(self):
        paths = get_paths(self.app)
        self.stage_dir = os.path.join(paths["input"], self.stage)
        os.makedirs(self.stage_dir, exist_ok=True)

        yield Header()
        yield Static(self.stage.upper())
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

    def compose(self):
        yield Header()
        yield Static("nano")
        yield Button("START", id="start")
        yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        paths = get_paths(self.app)
        stage_dir = os.path.join(paths["input"], self.stage)

        if e.button.id == "start":
            filepath = os.path.join(stage_dir, "newfile.in")
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
        yield Static(self.directory)

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

    def compose(self):
        paths = get_paths(self.app)
        is_output = self.filepath.startswith(paths["result"])

        yield Header()
        with Horizontal():
            with Vertical():
                yield Static(self.filepath)
                if not is_output:
                    yield Button("EDIT", id="edit")
                yield Button("BACK", id="back")

            with Vertical():
                try:
                    with open(self.filepath) as f:
                        content = f.read()
                except:
                    content = "[BINARY]"
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
        yield Header()
        yield Vertical(
            Button("RUN", id="run"),
            Button("QUEUE", id="queue"),
            Button("ANALYSIS", id="analisis"),
            Button("CANCEL", id="cancel"),
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
            paths = get_paths(self.app)

            sys.path.append(paths["analisis"])
            module = importlib.import_module(f"{self.stage.upper()}_ANALYSIS")
            importlib.reload(module)

            stage_dir = os.path.join(paths["result"], self.stage)
            os.makedirs(stage_dir, exist_ok=True)

            module.main(stage_dir)

        elif e.button.id == "back":
            self.app.pop_screen()

# ===================== INPUT SELECTOR =====================

class StageInputSelector(Screen):
    def __init__(self, stage):
        super().__init__()
        self.stage = stage
        self.file_map = {}

    def compose(self):
        paths = get_paths(self.app)
        stage_input_dir = os.path.join(paths["input"], self.stage)

        yield Header()
        yield Static("select input")

        with Vertical():
            if os.path.exists(stage_input_dir):
                for i, f in enumerate(sorted(os.listdir(stage_input_dir))):
                    if f.endswith(".in"):
                        path = os.path.join(stage_input_dir, f)
                        self.file_map[f"id_{i}"] = path
                        yield Button(f, id=f"id_{i}")

            yield Button("BACK", id="back")

        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()

        elif e.button.id in self.file_map:
            result = run_sbatch(self.stage, self.file_map[e.button.id], self.app)
            self.app.notify(result)
            self.app.pop_screen()

# ===================== CANCEL =====================

class CancelJobSelector(Screen):
    def compose(self):
        yield Header()
        self.jobs = get_user_jobs(self.app)

        with Vertical():
            if not self.jobs:
                yield Static("no jobs")
            else:
                for i, (jobid, jobname) in enumerate(self.jobs):
                    yield Button(f"{jobid} {jobname}", id=f"job_{i}")

            yield Button("BACK", id="back")

        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id.startswith("job_"):
            idx = int(e.button.id.split("_")[1])
            jobid, _ = self.jobs[idx]
            run_shell(f"scancel {jobid}", self.app)
            self.app.pop_screen()

# ===================== QUEUE =====================

class QueueScreen(Screen):
    def compose(self):
        yield Header()
        yield TextArea(run_shell("squeue -u $USER", self.app), read_only=True)
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
            Button("RELAX", id="relax"),
            Button("JOIN", id="join"),
            Button("HEATHOLD", id="heathold"),
            Button("STATISTICS", id="statistics"),
            Button("BACK", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        else:
            paths = get_paths(self.app)
            self.app.push_screen(FileBrowser(os.path.join(paths["result"], e.button.id)))

# ===================== APP =====================

class LammpsUI(App):
    current_sim = None

    CSS = """
    Vertical { align: center middle; }
    Button { width: 40; margin: 1; }
    """

    def on_mount(self):
        self.push_screen(MainMenu())

if __name__ == "__main__":
    LammpsUI().run()
