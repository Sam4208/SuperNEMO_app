import os

def create_desktop_icon():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop_path, "SuperNEMO_GUI.desktop")
    current_directory = os.path.abspath(os.getcwd())  # Get the current directory

    with open(shortcut_path, "w") as shortcut:
        shortcut.write(
            "[Desktop Entry]\n"
            "Version=1.0\n"
            "Type=Application\n"
            "Name=SuperNEMO_GUI\n"
            f"Exec=python3 {current_directory}/main_gui.py\n"  # Use the current directory
            f"Icon={current_directory}/logo.png\n"
            "Terminal=false\n"
        )

    print(f"Desktop icon created at {shortcut_path}")

if __name__ == "__main__":
    create_desktop_icon()