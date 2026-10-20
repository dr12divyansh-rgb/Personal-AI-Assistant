from pywinauto import Desktop
import subprocess
import time


print("Opening Windows Clock...")

subprocess.Popen(
    [
        "explorer.exe",
        "shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"
    ]
)

time.sleep(3)


clock = Desktop(
    backend="uia"
).window(
    title="Clock"
)

print("Found Clock")


# Open Timer
timer_button = clock.child_window(
    auto_id="TimerButton",
    control_type="ListItem"
)

timer_button.click_input()

time.sleep(1)


# Click Add New Timer
add_timer_button = clock.child_window(
    auto_id="AddTimerButton",
    control_type="Button"
)

print("Opening Add Timer...")

add_timer_button.click_input()

time.sleep(1)


print("\n" + "=" * 60)
print("ADD TIMER CONTROLS")
print("=" * 60)


def show_controls(control, level=0):

    try:

        indent = "  " * level

        print(
            f"{indent}"
            f"Type={control.element_info.control_type} | "
            f"Name='{control.window_text()}' | "
            f"AutomationId='{control.element_info.automation_id}'"
        )

        for child in control.children():

            show_controls(
                child,
                level + 1
            )

    except Exception as e:

        print(
            "Error:",
            e
        )


show_controls(clock)


print("\n" + "=" * 60)
print("END")
print("=" * 60)