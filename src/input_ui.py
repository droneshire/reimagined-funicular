import tkinter as tk
import typing as T
from tkinter import ttk


class SimpleInputForm:

    def __init__(self, verbose: bool = True):
        self.root = tk.Tk()
        self.inputs: T.Dict[str, str] = {}
        self.verbose = verbose
        self.root.title("User Form")

        self.location_entry: T.Optional[ttk.Entry] = None
        self.adults_spinbox: T.Optional[ttk.Spinbox] = None
        self.date_entry: T.Optional[ttk.Entry] = None
        self.duration_spinbox: T.Optional[ttk.Spinbox] = None
        self.group_entry: T.Optional[ttk.Entry] = None
        self.description_text: T.Optional[tk.Text] = None

    def setup(self) -> None:
        main_frame = ttk.Frame(self.root)
        main_frame.grid(padx=10, pady=10, sticky="ew")

        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text="Location: *").grid(row=0, column=0, sticky="w")
        self.location_entry = ttk.Entry(main_frame)
        self.location_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(main_frame, text="Number of Adults: *").grid(row=1, column=0, sticky="w")
        self.adults_spinbox = ttk.Spinbox(main_frame, from_=1, to=100)
        self.adults_spinbox.grid(row=1, column=1, sticky="ew")

        ttk.Label(main_frame, text="Date of month: *").grid(row=2, column=0, sticky="w")
        self.date_entry = ttk.Entry(main_frame)
        self.date_entry.grid(row=2, column=1, sticky="ew")

        ttk.Label(main_frame, text="Durations (day): *").grid(row=3, column=0, sticky="w")
        self.duration_spinbox = ttk.Spinbox(main_frame, from_=1, to=30)
        self.duration_spinbox.grid(row=3, column=1, sticky="ew")

        ttk.Label(main_frame, text="Tell us about your group: *").grid(row=4, column=0, sticky="w")
        self.group_entry = ttk.Entry(main_frame)
        self.group_entry.grid(row=4, column=1, sticky="ew")

        ttk.Label(
            main_frame,
            text=(
                "Briefly describe the trip you envision including "
                "the group's interests in activities, food etc:"
            ),
        ).grid(row=5, column=0, sticky="nw", pady=(10, 0))
        self.description_text = tk.Text(main_frame, height=5)
        self.description_text.grid(row=5, column=1, sticky="ew")

        submit_button = ttk.Button(main_frame, text="FIND", command=self.on_submit)
        submit_button.grid(row=6, column=1, sticky="ew", pady=10)

    def on_submit(self) -> None:
        if (
            self.location_entry is None
            or self.adults_spinbox is None
            or self.date_entry is None
            or self.duration_spinbox is None
            or self.group_entry is None
            or self.description_text is None
        ):
            return
        location = self.location_entry.get()
        number_of_adults = self.adults_spinbox.get()
        date_of_month = self.date_entry.get()
        duration = self.duration_spinbox.get()
        group_info = self.group_entry.get()
        description = self.description_text.get("1.0", tk.END)

        self.inputs["location"] = location
        self.inputs["number_of_people"] = number_of_adults
        self.inputs["date"] = date_of_month
        self.inputs["duration_days"] = duration
        self.inputs["group_type"] = group_info
        self.inputs["description"] = description.strip()

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
        return self.inputs
