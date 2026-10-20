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


print("\nFinding Clock window...\n")

windows = Desktop(backend="uia").windows()

clock = None

for window in windows:

    try:
        title = window.window_text()

        if "clock" in title.lower():

            clock = window

            print("Found Clock:", title)

            break

    except Exception:
        pass


if clock is None:

    print("Clock window was not found.")
    exit()


print("\n" + "=" * 60)
print("CLOCK CONTROLS")
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
            "Error reading control:",
            e
        )


show_controls(clock)

print("\n" + "=" * 60)
print("END")
print("=" * 60)