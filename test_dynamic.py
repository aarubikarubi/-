import time
from core import GameMonitor, State
import setup_ui

class MockMonitor(GameMonitor):
    def __init__(self):
        super().__init__(config_path="test_config.json")
        self.running_procs = set()
        self.launched = []

    def load_config(self):
        self.games = [
            {"name": "App 1", "process_name": "app1.exe", "path": "path1"},
            {"name": "App 2", "process_name": "app2.exe", "path": "path2"}
        ]

    def is_process_running(self, process_name):
        return process_name in self.running_procs

    def launch_game(self, game_index):
        if game_index < len(self.games):
            name = self.games[game_index]['process_name']
            self.launched.append(name)
            print(f"[Mock] Launched {name}")

def run_test():
    monitor = MockMonitor()
    monitor.start()

    print("Test: Starting app 1...")
    monitor.running_procs.add("app1.exe")
    time.sleep(4)
    assert monitor.state.value == 1, f"Expected 1, got {monitor.state.value}"

    print("Test: Closing app 1...")
    monitor.running_procs.remove("app1.exe")
    time.sleep(4)
    assert monitor.state.value == 2, f"Expected 2, got {monitor.state.value}"
    assert "app2.exe" in monitor.launched, "app2.exe should be launched"

    monitor.running_procs.add("app2.exe")
    time.sleep(4)
    assert not monitor.waiting_for_launch

    print("Test: Closing app 2...")
    monitor.running_procs.remove("app2.exe")
    time.sleep(4)
    assert monitor.state == State.STANDBY, f"Expected STANDBY, got {monitor.state}"

    print("Test passed!")
    monitor.stop()

if __name__ == '__main__':
    run_test()
