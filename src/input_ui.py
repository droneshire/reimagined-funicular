import tkinter as tk
import typing as T
from tkinter import ttk


class SimpleInputForm:

    def __init__(self, verbose: bool = True):
        self.root = tk.Tk()
        self.inputs: T.Dict[str, str] = {}
        self.verbose = verbose
        self.root.title("User Form")

    def setup(self) -> None:
        main_frame = ttk.Frame(self.root)
        main_frame.grid(padx=10, pady=10, sticky="ew")

        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Location: *").grid(row=0, column=0, sticky="w")
        location_entry = ttk.Entry(main_frame)
        location_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(main_frame, text="Number of Adults: *").grid(row=1, column=0, sticky="w")
        adults_spinbox = ttk.Spinbox(main_frame, from_=1, to=100)
        adults_spinbox.grid(row=1, column=1, sticky="ew")

        ttk.Label(main_frame, text="Date of month: *").grid(row=2, column=0, sticky="w")
        date_entry = ttk.Entry(main_frame)
        date_entry.grid(row=2, column=1, sticky="ew")

        ttk.Label(main_frame, text="Durations (day): *").grid(row=3, column=0, sticky="w")
        duration_spinbox = ttk.Spinbox(main_frame, from_=1, to=30)
        duration_spinbox.grid(row=3, column=1, sticky="ew")

        ttk.Label(main_frame, text="Tell us about your group: *").grid(row=4, column=0, sticky="w")
        group_entry = ttk.Entry(main_frame)
        group_entry.grid(row=4, column=1, sticky="ew")

        ttk.Label(
            main_frame,
            text=(
                "Briefly describe the trip you envision including "
                "the group's interests in activities, food etc:"
            ),
        ).grid(row=5, column=0, sticky="nw", pady=(10, 0))
        description_text = tk.Text(main_frame, height=5)
        description_text.grid(row=5, column=1, sticky="ew")

        submit_button = ttk.Button(main_frame, text="FIND", command=self.on_submit)
        submit_button.grid(row=6, column=1, sticky="ew", pady=10)

    def on_submit(self) -> None:
        location = location_entry.get()
        number_of_adults = adults_spinbox.get()
        date_of_month = date_entry.get()
        duration = duration_spinbox.get()
        group_info = group_entry.get()
        description = description_text.get("1.0", tk.END)

        inputs["location"] = location
        inputs["number_of_people"] = number_of_adults
        inputs["date"] = date_of_month
        inputs["duration_days"] = duration
        inputs["group_type"] = group_info
        inputs["description"] = description.strip()

        if self.verbose:
            print("Form submitted with the following details:")
            print(f"Location: {location}")
            print(f"Number of Adults: {number_of_adults}")
            print(f"Date of Month: {date_of_month}")
            print(f"Duration (days): {duration}")
            print(f"Group Information: {group_info}")
            print(f"Description: {description.strip()}")
            
        self.root.destroy()

    def run_form(self) -> T.Dict[str, str]:
        self.root.mainloop()
        return inputs
