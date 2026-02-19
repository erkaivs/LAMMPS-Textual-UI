from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, TextArea
from textual.containers import Vertical, Horizontal
import subprocess
import os
import sys
import importlib

# ===================== PATH =====================
BASE_DIR = os.path.expanduser("~/workspace/lammps_ui")
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
RESULT_DIR = os.path.join(BASE_DIR, "result")
ANALYSIS_DIR = os.path.join(BASE_DIR, "analisis")
SUBMIT_DIR = os.path.join(BASE_DIR, "submit")
LMP_PROG = os.path.expanduser("~/bin/lmp_nero")

sys.path.append(ANALYSIS_DIR)

# ===================== UTIL =====================
def run_shell(cmd: str) -> str:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip() or r.stderr.strip()

def run_sbatch(stage: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    template = os.path.join(SUBMIT_DIR, "submit.template")
    generated = os.path.join(SUBMIT_DIR, "submit.generated.bash")

    with open(template) as f:
        txt = f.read()

    txt = (
        txt.replace("JOBNAME", stage)
           .replace("NTASKS", "12")
           .replace("LMP_PROG", LMP_PROG)
           .replace("INPUT_FILE", os.path.join(INPUT_DIR, f"{stage}.in"))
    )

    with open(generated, "w") as f:
        f.write(txt)

    return run_shell(f"sbatch {generated}")

# ===================== MAIN MENU =====================
class MainMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Button("FILES", id="files"),
            Button("RELAX", id="relax"),
            Button("JOIN", id="join"),
            Button("HEATHOLD", id="heathold"),
            Button("RESULT", id="result"),
        )
        yield Footer()

    def on_button_pressed(self, e):
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
            Button("NEW FILE", id="new"),
            Button("OPEN FILES", id="open"),
            Button("REMOVE FILES", id="remove"),
            Button("BACK", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "new":
            self.app.push_screen(NewFile())
        elif e.button.id == "open":
            self.app.push_screen(FileBrowser(INPUT_DIR))
        elif e.button.id == "remove":
            self.app.push_screen(RemoveFileBrowser(INPUT_DIR))
        elif e.button.id == "back":
            self.app.pop_screen()

# ===================== NEW FILE =====================
class NewFile(Screen):
    def compose(self):
        yield Header()
        yield Static(
            "NEW FILE\n\n"
            "Nano will open.\n"
            "Save with Ctrl+O\n"
            "Rename file (example: relax.in)\n"
            "Exit nano to return."
        )
        yield Button("START", id="start")
        yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "start":
            with self.app.suspend():
                subprocess.run(["nano", os.path.join(INPUT_DIR, "newfile.in")])
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

# ===================== FILE VIEW =====================
class FileView(Screen):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.is_output = filepath.startswith(OUTPUT_DIR) or filepath.startswith(RESULT_DIR)

    def compose(self):
        yield Header()
        with Horizontal():
            with Vertical():
                yield Static(f"FILE:\n{self.filepath}")
                if not self.is_output:
                    yield Button("EDIT (vim)", id="edit")
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

# ===================== REMOVE FILE FLOW =====================
class RemoveFileBrowser(Screen):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.file_map = {}

    def compose(self):
        yield Header()
        yield Static("REMOVE FILES")
        with Vertical():
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
            self.app.push_screen(RemoveFileView(self.file_map[e.button.id]))

class RemoveFileView(Screen):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def compose(self):
        yield Header()
        with Horizontal():
            with Vertical():
                yield Static(f"FILE:\n{self.filepath}")
                yield Button("REMOVE", id="remove")
                yield Button("BACK", id="back")
            with Vertical():
                yield TextArea(open(self.filepath).read(), read_only=True)
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id == "remove":
            self.app.push_screen(ConfirmDelete(self.filepath))

class ConfirmDelete(Screen):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def compose(self):
        yield Header()
        yield Static("ARE YOU SURE?\n\nYou can't recover this file.")
        with Horizontal():
            yield Button("YES", id="yes")
            yield Button("NO", id="no")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "yes":
            os.remove(self.filepath)
            self.app.pop_screen()
            self.app.pop_screen()
            self.app.push_screen(RemoveFileBrowser(INPUT_DIR))
        elif e.button.id == "no":
            self.app.pop_screen()

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
            self.app.notify(run_sbatch(self.stage))

        elif e.button.id == "queue":
            self.app.push_screen(QueueScreen())

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

            self.app.notify(f"ANALYSIS {self.stage.upper()} SAVED IN RESULT.")

        elif e.button.id == "cancel":
            self.app.notify(run_shell(f"scancel -n {self.stage}"))

        elif e.button.id == "back":
            self.app.pop_screen()

# ===================== QUEUE SCREEN =====================
class QueueScreen(Screen):
    def compose(self):
        yield Header()
        yield TextArea(run_shell("squeue -u $USER"), read_only=True)
        yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()

# ===================== RESULT SUB MENU =====================
class ResultStageMenu(Screen):
    def compose(self):
        yield Header()
        yield Vertical(
            Button("RELAX RESULT", id="relax"),
            Button("JOIN RESULT", id="join"),
            Button("HEATHOLD RESULT", id="heathold"),
            Button("BACK", id="back"),
        )
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        else:
            self.app.push_screen(ResultFileMenu(os.path.join(RESULT_DIR, e.button.id)))

class ResultFileMenu(Screen):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def compose(self):
        yield Header()
        with Vertical():
            if not os.path.exists(self.directory):
                yield Button("BACK", id="back")
            else:
                for i, f in enumerate(sorted(os.listdir(self.directory))):
                    yield Button(f, id=f"r_{i}")
                yield Button("BACK", id="back")
        yield Footer()

    def on_button_pressed(self, e):
        if e.button.id == "back":
            self.app.pop_screen()
        elif e.button.id.startswith("r_"):
            idx = int(e.button.id.split("_")[1])
            fname = sorted(os.listdir(self.directory))[idx]
            self.app.push_screen(FileView(os.path.join(self.directory, fname)))

# ===================== APP =====================
class LammpsUI(App):
    CSS = """
    Vertical {
        align: center middle;
    }
    Button {
        width: 42;
        margin: 1;
    }
    """

    def on_mount(self):
        self.push_screen(MainMenu())

if __name__ == "__main__":
    LammpsUI().run()
