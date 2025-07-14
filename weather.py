import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
import datetime

# Constants
API_KEY = '0ae9f868e7d775bf6bac7968579366f1'  # Replace with your API key
BASE_URL = 'https://api.openweathermap.org/data/2.5/'

# App Class
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤 Arcade Weather")
        self.root.geometry("800x700")
        self.root.configure(bg="#0f172a")

        self.city_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="🌦 Arcade Weather Station", font=("Segoe UI", 22, "bold"),
                 bg="#0f172a", fg="#38bdf8").pack(pady=15)

        # Input Field
        input_frame = tk.Frame(self.root, bg="#1e293b")
        input_frame.pack(pady=10)

        tk.Entry(input_frame, textvariable=self.city_var, font=("Segoe UI", 14), width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(input_frame, text="Get Weather", font=("Segoe UI", 12, "bold"), bg="#38bdf8", fg="white",
                  command=self.fetch_weather).pack(side=tk.LEFT, padx=5)

        # Save button
        self.save_button = tk.Button(self.root, text="💾 Save Report", font=("Segoe UI", 12),
                                     command=self.save_report, bg="#10b981", fg="white", state=tk.DISABLED)
        self.save_button.pack(pady=5)

        # Current Weather
        self.weather_frame = tk.Frame(self.root, bg="#0f172a")
        self.weather_frame.pack(pady=10)

        # Forecast
        self.forecast_frame = tk.Frame(self.root, bg="#0f172a")
        self.forecast_frame.pack(pady=10)

    def fetch_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showerror("Input Error", "City name cannot be empty.")
            return

        try:
            weather = requests.get(f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric").json()
            forecast = requests.get(f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric").json()

            if str(weather.get("cod")) != "200":
                raise Exception(weather.get("message", "City not found."))

            self.show_current_weather(weather)
            self.show_forecast(forecast)
            self.latest_weather = weather
            self.latest_forecast = forecast
            self.save_button.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve data: {e}")

    def show_current_weather(self, data):
        for widget in self.weather_frame.winfo_children():
            widget.destroy()

        main = data['main']
        wind = data['wind']
        weather = data['weather'][0]
        sys_data = data['sys']

        # Weather Icon
        icon_url = f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png"
        icon_img = ImageTk.PhotoImage(Image.open(BytesIO(requests.get(icon_url).content)).resize((80, 80)))

        tk.Label(self.weather_frame, image=icon_img, bg="#0f172a").grid(row=0, column=0, rowspan=6, padx=10)
        self.weather_icon = icon_img  # keep ref

        labels = [
            ("📍 Location", f"{data['name']}, {sys_data['country']}"),
            ("🌡 Temperature", f"{main['temp']}°C (Feels like {main['feels_like']}°C)"),
            ("☁ Condition", weather['description'].capitalize()),
            ("💧 Humidity", f"{main['humidity']}%"),
            ("🌬 Wind Speed", f"{wind['speed']} m/s"),
            ("🕒 Updated", datetime.datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M UTC')),
        ]

        for i, (label, value) in enumerate(labels):
            tk.Label(self.weather_frame, text=label + ":", font=("Segoe UI", 11, "bold"),
                     bg="#0f172a", fg="#facc15").grid(row=i, column=1, sticky="w", padx=5)
            tk.Label(self.weather_frame, text=value, font=("Segoe UI", 11),
                     bg="#0f172a", fg="white").grid(row=i, column=2, sticky="w")

    def show_forecast(self, data):
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.forecast_frame, bg="#0f172a", width=750, height=250, highlightthickness=0)
        scroll_frame = tk.Frame(canvas, bg="#0f172a")
        scrollbar = ttk.Scrollbar(self.forecast_frame, orient="horizontal", command=canvas.xview)

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack()
        scrollbar.pack(fill="x")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for i, item in enumerate(data['list'][:20]):
            dt_txt = item['dt_txt']
            temp = f"{item['main']['temp']}°C"
            desc = item['weather'][0]['description'].capitalize()
            icon_url = f"http://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png"
            icon_img = ImageTk.PhotoImage(Image.open(BytesIO(requests.get(icon_url).content)).resize((50, 50)))

            card = tk.Frame(scroll_frame, bg="#1e293b", bd=1, relief="ridge")
            card.grid(row=0, column=i, padx=5, pady=5)

            tk.Label(card, image=icon_img, bg="#1e293b").pack()
            tk.Label(card, text=dt_txt.split()[0] + "\n" + dt_txt.split()[1], font=("Segoe UI", 9),
                     bg="#1e293b", fg="#38bdf8").pack()
            tk.Label(card, text=temp, font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="white").pack()
            tk.Label(card, text=desc, font=("Segoe UI", 9), bg="#1e293b", fg="#e2e8f0", wraplength=100,
                     justify="center").pack()
            card.image = icon_img

    def save_report(self):
        if not hasattr(self, 'latest_weather') or not hasattr(self, 'latest_forecast'):
            return

        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file", "*.txt")])
        if not file:
            return

        try:
            with open(file, "w", encoding="utf-8") as f:
                data = self.latest_weather
                forecast = self.latest_forecast
                main = data['main']
                wind = data['wind']
                weather = data['weather'][0]

                f.write(f"Weather Report for {data['name']}, {data['sys']['country']}\n")
                f.write("-" * 50 + "\n")
                f.write(f"Temperature: {main['temp']}°C (Feels like {main['feels_like']}°C)\n")
                f.write(f"Condition: {weather['description'].capitalize()}\n")
                f.write(f"Humidity: {main['humidity']}%\n")
                f.write(f"Wind: {wind['speed']} m/s\n")
                f.write(f"Updated: {datetime.datetime.utcfromtimestamp(data['dt'])}\n\n")
                f.write("5-Day Forecast:\n")
                for item in forecast['list']:
                    f.write(f"{item['dt_txt']} - {item['main']['temp']}°C - {item['weather'][0]['description'].capitalize()}\n")
            messagebox.showinfo("Saved", "✅ Report saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

# Main Run
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()