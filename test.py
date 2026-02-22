import time
from core import GameMonitor, State

class MockMonitor(GameMonitor):
    def __init__(self):
        super().__init__(config_path="config.json")
        self.running_procs = set()
        self.launched = []

    def is_process_running(self, process_name):
        return process_name in self.running_procs

    def launch_game(self, game_index):
        if game_index < len(self.games):
            name = self.games[game_index]['process_name']
            self.launched.append(name)
            # Simulate immediate launch by adding it to running
            # Though in real life it might take time, we simulate it
            print(f"[Mock] Launched {name}")

def run_test():
    monitor = MockMonitor()
    monitor.games = [
        {"name": "Game 1", "process_name": "game1.exe", "path": "g1"},
        {"name": "Game 2", "process_name": "game2.exe", "path": "g2"},
        {"name": "Game 3", "process_name": "game3.exe", "path": "g3"}
    ]
    monitor.start()

    print("Test: Starting game 1...")
    monitor.running_procs.add("game1.exe")
    time.sleep(4)
    assert monitor.state == State.STAR_RAIL, f"Expected STAR_RAIL, got {monitor.state}"

    print("Test: Closing game 1...")
    monitor.running_procs.remove("game1.exe")
    time.sleep(4)
    assert monitor.state == State.GENSHIN, f"Expected GENSHIN, got {monitor.state}"
    assert "game2.exe" in monitor.launched, "game2.exe should be launched"

    # Simulate game 2 actually showing up
    monitor.running_procs.add("game2.exe")
    time.sleep(4)
    # The flag should be cleared
    assert not monitor.waiting_for_launch

    print("Test: Closing game 2...")
    monitor.running_procs.remove("game2.exe")
    time.sleep(4)
    assert monitor.state == State.WUTHERING_WAVES, f"Expected WUTHERING_WAVES, got {monitor.state}"
    assert "game3.exe" in monitor.launched, "game3.exe should be launched"

    # Simulate game 3 showing up
    monitor.running_procs.add("game3.exe")
    time.sleep(4)
    assert not monitor.waiting_for_launch

    print("Test: Closing game 3...")
    monitor.running_procs.remove("game3.exe")
    time.sleep(4)
    assert monitor.state == State.STANDBY, f"Expected STANDBY, got {monitor.state}"

    print("Test passed!")
    monitor.stop()

if __name__ == '__main__':
    run_test()
