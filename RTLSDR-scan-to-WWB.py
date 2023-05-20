import tkinter as tk
import xml.etree.ElementTree as ET
import ctypes
from tkinter import filedialog, messagebox
from ctypes import wintypes

# Constants required for the Windows API calls
SM_CXSCREEN = 0
SM_CYSCREEN = 1
SPI_GETWORKAREA = 48

# Message type values
error_fade_delay = 5000 #ms
success_fade_delay = 2000 #ms

# Retrieve the screen dimensions
screen_width = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
screen_height = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)

# Retrieve the work area dimensions (excluding taskbar)
work_area = ctypes.wintypes.RECT()
ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(work_area), 0)
work_area_height = work_area.bottom - work_area.top

# Calculate the system tray height
system_tray_height = screen_height - work_area_height

# Create a hidden Tkinter window
window = tk.Tk()
window.withdraw()

# Open dialog to select a file
file_path = filedialog.askopenfilename(title="RTLSDR scan to WWB converter", filetypes=[("WWB Scan Files", "*.sdb2")])

success_window = None  # Initialize the success_window variable

def quit_application(event):
    window.quit()

if file_path != '':
    try:
        # Load the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Define the modification factor
        modification_factorPRE = +30
        multiplication_factor = 4
        modification_factorPOST = -85

        # Modify the numbers between the <v> tags
        for v_element in root.iter("v"):
            current_value = float(v_element.text)
            modified_value = current_value + modification_factorPRE
            modified_value = modified_value * multiplication_factor
            modified_value = modified_value + modification_factorPOST
            v_element.text = str(modified_value)

        # Save the modified XML back to the file
        tree.write(file_path, encoding="UTF-8", xml_declaration=True)

        # Define the message content and style
        message = "File modified successfully."
        message_color = "green"
        fade_delay = success_fade_delay  # Delay before starting the fade-out (in milliseconds)

    except Exception as e:
        # If there's an error, display the error message instead
        message = f"Error modifying file:\n{str(e)}"
        message_color = "darkred"
        fade_delay = error_fade_delay  # Delay before starting the fade-out (in milliseconds)

else:
    # No file selected
    message = "No file was selected."
    message_color = "darkred"
    fade_delay = error_fade_delay  # Delay before starting the fade-out (in milliseconds)

if True:

    # Create a Toplevel window for the success message
    success_window = tk.Toplevel()
    success_window.overrideredirect(True)  # Remove window decorations
    success_window.attributes('-topmost', True)  # Keep the window on top

    # Bind the quit_application function to the left mouse button click event on the success window
    success_window.bind("<ButtonRelease-1>", quit_application)


    # Get the screen width and height
    screen_width = success_window.winfo_screenwidth()
    screen_height = success_window.winfo_screenheight()

    # Define the header text
    header_text = "RTLSDR Scan to WWB"

    # Create a label for the header
    header_label = tk.Label(success_window, text=header_text, padx=10, pady=5, bg="gray", fg="white",
                            font=("Arial", 10, "bold"), anchor='w')
    header_label.pack(fill=tk.BOTH)

    # Create a label with the message and styling
    message_label = tk.Label(success_window, text=message, padx=20, pady=10, bg=message_color, fg="white",
                             font=("Arial", 12, "bold"))
    message_label.pack(fill=tk.BOTH, expand=True)

    # Calculate the maximum width of the message and header
    text_width = max(header_label.winfo_reqwidth(), message_label.winfo_reqwidth())
    max_width = screen_width - 100  # Set a maximum width for the window

    # Adjust the width if it exceeds the maximum
    window_width = min(text_width + 40, max_width)  # Add padding to the width

    # Calculate the window height based on the message length
    text_height = header_label.winfo_reqheight() + message_label.winfo_reqheight()
    window_height = text_height + 30  # Add padding to the height

    # Set the window position and dimensions
    x = screen_width - window_width - 5  # 10 is the margin
    y = screen_height - window_height - system_tray_height - 5  # 10 is the margin
    success_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Create a close button for the success window
    close_button = tk.Label(success_window, text="\U0001F5D9", font=("Arial", 12, "bold"), bg="gray", fg="white")
    close_button.place(x=window_width-20, y=0)

    # Hide the close button initially
    close_button.place_forget()


    # Update the window to calculate the label sizes
    success_window.update_idletasks()

    # Change the cursor to a hand pointer on hover
    success_window.bind("<Enter>", lambda event: mousehover())
    success_window.bind("<Leave>", lambda event: mouseleave())

    def mousehover():
        success_window.config(cursor="hand2")
        close_button.place(x=window_width-20, y=-1)

    def mouseleave():
        success_window.config(cursor="")
        close_button.place_forget()

    # Animate the fade-out effect
    opacity = [1.0]
    fade_duration = 2000  # Duration of the fade-out effect (in milliseconds)
    fade_steps = 240  # Number of steps in the fade-out effect

    # Function to update the opacity and destroy the window
    def fade_out():
        if opacity[0] > 0:
            success_window.attributes("-alpha", opacity[0])
            opacity[0] -= 1 / fade_steps
            success_window.after(int(fade_duration / fade_steps), fade_out)
        else:
            window.quit()

    # Start the fade-out effect after the specified delay
    success_window.after(fade_delay, fade_out)

# Run the Tkinter event loop
window.mainloop()
