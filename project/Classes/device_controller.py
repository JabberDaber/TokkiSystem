class DeviceController:
    def __init__(self, root):
        self.root = root
        self.states = {}
        self.lock_timers = {}

    def get_state(self, device):
        return self.states.get(device, False)

    def set_state(self, device, enabled):
        timer = self.lock_timers.pop(device, None)
        if timer is not None:
            self.root.after_cancel(timer)
        self.states[device] = bool(enabled)
        print(f"[SIMULATED] {device}: {'ON / UNLOCKED' if enabled else 'OFF / LOCKED'}")

    def unlock_for(self, device, milliseconds=5000, on_lock=None):
        self.set_state(device, True)

        def automatic_lock():
            self.lock_timers.pop(device, None)
            self.states[device] = False
            print(f"[SIMULATED] {device}: AUTOMATICALLY LOCKED")
            if on_lock is not None:
                on_lock()

        self.lock_timers[device] = self.root.after(milliseconds, automatic_lock)
