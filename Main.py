import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import json
import os

# API Interaction Module
def decode_vin(vin, model_year=None):
    """Fetch vehicle details using the VIN decoder endpoint."""
    base_url = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/"
    params = {"format": "json"}
    if model_year:
        params["modelyear"] = model_year
    response = requests.get(f"{base_url}{vin}", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Report Generation Module
def generate_html_report(data, file_path):
    """Generate an HTML report from the API response data."""
    with open(file_path, "w") as file:
        file.write("<html><head><title>VIN Report</title></head><body>")
        file.write("<h1>Vehicle Information Report</h1>")
        file.write("<table border='1'>")
        file.write("<tr><th>Field</th><th>Value</th></tr>")
        for item in data.get('Results', []):
            file.write(f"<tr><td>{item['Variable']}</td><td>{item['Value'] or 'N/A'}</td></tr>")
        file.write("</table>")
        file.write("</body></html>")

# GUI Module
class AppGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Vehicle Information Decoder")
        self.window.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        # Input Fields
        ttk.Label(self.window, text="VIN:").grid(row=0, column=0, padx=10, pady=10)
        self.vin_entry = ttk.Entry(self.window, width=30)
        self.vin_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Model Year (optional):").grid(row=1, column=0, padx=10, pady=10)
        self.model_year_entry = ttk.Entry(self.window, width=30)
        self.model_year_entry.grid(row=1, column=1, padx=10, pady=10)

        # Buttons
        ttk.Button(self.window, text="Decode VIN", command=self.decode_vin_button).grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(self.window, text="Clear", command=self.clear_inputs).grid(row=3, column=0, padx=10, pady=10)
        ttk.Button(self.window, text="Export Report", command=self.export_report).grid(row=3, column=1, padx=10, pady=10)

        # Output Display
        self.output_text = tk.Text(self.window, wrap=tk.WORD, height=10, width=70)
        self.output_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        self.output_text.insert(tk.END, "Decoded information will appear here.")

    def decode_vin_button(self):
        vin = self.vin_entry.get().strip()
        model_year = self.model_year_entry.get().strip()
        if not vin:
            messagebox.showerror("Error", "VIN is required.")
            return

        try:
            data = decode_vin(vin, model_year)
            self.display_results(data)
            self.api_response = data  # Store the data for report generation
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decode VIN: {e}")

    def display_results(self, data):
        self.output_text.delete(1.0, tk.END)
        if 'Results' in data:
            for item in data['Results']:
                self.output_text.insert(tk.END, f"{item['Variable']}: {item['Value'] or 'N/A'}\n")
        else:
            self.output_text.insert(tk.END, "No results found.")

    def clear_inputs(self):
        self.vin_entry.delete(0, tk.END)
        self.model_year_entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Decoded information will appear here.")

    def export_report(self):
        if not hasattr(self, 'api_response') or not self.api_response:
            messagebox.showerror("Error", "No data to export. Please decode a VIN first.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".html",
                                                 filetypes=[("HTML files", "*.html")])
        if file_path:
            try:
                generate_html_report(self.api_response, file_path)
                messagebox.showinfo("Success", f"Report saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")

    def run(self):
        self.window.mainloop()

# Main Entry Point
if __name__ == "__main__":
    app = AppGUI()
    app.run()
