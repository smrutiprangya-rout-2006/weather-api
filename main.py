import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import requests
from PIL import Image, ImageTk
from io import BytesIO
import datetime

API_KEY = '0ae9f868e7d775bf6bac7968579366f1'
BASE_URL = 'https://api.openweathermap.org/data/2.5/'

# ---------- Fetching Weather ----------
def get_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    return res.json()

def get_forecast(city):
    url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"
    res = requests.get(url)
    return res.json()

# ---------- GUI ----------
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌦 Arcade Weather")
        self.root.geometry("650x600")
        self.root.configure(bg="#111827")

        # Title
        title = tk.Label(root, text="🌤 Arcade Weather App", font=("Helvetica", 20, "bold"), bg="#111827", fg="#38bdf8")
        title.pack(pady=10)

        # Input
        input_frame = tk.Frame(root, bg="#1f2937")
        input_frame.pack(pady=10)

        self.city_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.city_var, font=("Helvetica", 14), width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(input_frame, text="Get Weather", command=self.fetch_weather, font=("Helvetica", 12),
                  bg="#38bdf8", fg="#ffffff", relief="flat").pack(side=tk.LEFT)

        # Output frames
        self.output_frame = tk.Frame(root, bg="#111827")
        self.output_frame.pack(pady=10)

        self.forecast_frame = tk.Frame(root, bg="#111827")
        self.forecast_frame.pack(pady=5)

    def fetch_weather(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showerror("Input Error", "Please enter a city name.")
            return

        try:
            weather = get_weather(city)
            forecast = get_forecast(city)

            if str(weather.get("cod")) != "200":
                raise ValueError(weather.get("message", "City not found."))

            self.display_weather(weather)
            self.display_forecast(forecast)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch weather: {e}")

    def display_weather(self, data):
        for widget in self.output_frame.winfo_children():
            widget.destroy()

        main = data['main']
        weather = data['weather'][0]
        wind = data['wind']
        sys_data = data['sys']

        city_country = f"{data['name']}, {sys_data['country']}"
        temp = f"{main['temp']}°C (Feels like {main['feels_like']}°C)"
        description = weather['description'].capitalize()
        humidity = f"{main['humidity']}%"
        wind_speed = f"{wind['speed']} m/s"
        updated = datetime.datetime.utcfromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M UTC')

        # Weather Icon
        icon_url = f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png"
        img_data = requests.get(icon_url).content
        icon_img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
        icon_label = tk.Label(self.output_frame, image=icon_img, bg="#111827")
        icon_label.image = icon_img  # keep reference
        icon_label.grid(row=0, column=0, rowspan=6, padx=10)

        # Weather Text
        labels = [
            ("📍 Location:", city_country),
            ("🌡 Temperature:", temp),
            ("☁ Weather:", description),
            ("💧 Humidity:", humidity),
            ("🌬 Wind Speed:", wind_speed),
            ("🕒 Updated:", updated),
        ]

        for i, (label, val) in enumerate(labels):
            tk.Label(self.output_frame, text=label, font=("Helvetica", 12, "bold"), bg="#111827", fg="#facc15").grid(row=i, column=1, sticky="w", padx=5, pady=2)
            tk.Label(self.output_frame, text=val, font=("Helvetica", 12), bg="#111827", fg="white").grid(row=i, column=2, sticky="w", padx=5)

    def display_forecast(self, data):
        for widget in self.forecast_frame.winfo_children():
            widget.destroy()

        if str(data.get("cod")) != "200":
            return

        canvas = tk.Canvas(self.forecast_frame, bg="#111827", height=200, bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.forecast_frame, orient="horizontal", command=canvas.xview)
        scroll_frame = tk.Frame(canvas, bg="#111827")

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(xscrollcommand=scrollbar.set)

        canvas.pack(fill="x")
        scrollbar.pack(fill="x")

        for i, item in enumerate(data["list"][:16]):  # Next ~2.5 days
            dt = item["dt_txt"]
            temp = f"{item['main']['temp']}°C"
            desc = item["weather"][0]["description"].capitalize()
            icon_url = f"http://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png"
            img_data = requests.get(icon_url).content
            icon = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize((50, 50)))

            card = tk.Frame(scroll_frame, bg="#1e293b", bd=1, relief="raised")
            card.grid(row=0, column=i, padx=5, pady=5)
            tk.Label(card, image=icon, bg="#1e293b").pack()
            card.image = icon
            tk.Label(card, text=dt.split()[1][:5], bg="#1e293b", fg="white").pack()
            tk.Label(card, text=temp, bg="#1e293b", fg="#38bdf8", font=("Helvetica", 10, "bold")).pack()
            tk.Label(card, text=desc, bg="#1e293b", fg="white", wraplength=100, justify="center").pack()

# ---------- Main ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()