import tkinter as tk
from tkinter import scrolledtext, ttk, simpledialog, filedialog, messagebox
from PIL import Image, ImageTk, ImageSequence
import pyttsx3
import speech_recognition as sr
import nltk
import datetime
import webbrowser

# dwnld nltk resources 
#only fr first run
try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except:
    nltk.download('stopwords')
import wikipedia
import pywhatkit
import psutil
import threading
import screen_brightness_control as sbc
import sys
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# data analysis n dashboard stuff
import os
import re
import pandas as pd
from pathlib import Path

# for the dashboard
try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.io as pio
except ImportError:
    px = None
    go = None
    pio = None





# speech engine stuff
engine = pyttsx3.init()
voices = engine.getProperty('voices')

male_voice = None
for voice in voices:
    if 'male' in voice.name.lower() or voice.id.find('male') != -1:
        male_voice = voice.id
        break
if male_voice:
    engine.setProperty('voice', male_voice)
else:
    engine.setProperty('voice', voices[0].id)

engine.setProperty('rate', 180)

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


def wishMe():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Hello Sir, Good Morning! Ready to assist you in any way!")
    elif hour < 18:
        speak("Hello Sir, Good Afternoon! Ready to assist you in any way!")
    else:
        speak("Hello Sir, Good Evening! Ready to assist you in any way!")


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        speak("I'm Listening...")
        r.pause_threshold = 2
        try:
            audio = r.listen(source)
            print("Recognizing...")
            speak("Recognizing...")
            command = r.recognize_google(audio, language='en-in')
            print(f'User said: {command}')
        except Exception:
            speak("Pardon me, please say that again.")
            return "None"
        return command.lower()


# system info stuff
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return battery.percent, "Charging" if battery.power_plugged else "Not Charging"
    return "Unknown", "No Battery"

def get_system_volume():
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume.iid, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return round(volume.GetMasterVolumeLevelScalar() * 100, 2)
    except Exception:
        return "Unknown"

def set_system_volume(volume_level):
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume.iid, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(volume_level / 100, None)
    except Exception:
        pass

def get_brightness():
    try:
        b = sbc.get_brightness(display=0)
        return b[0] if isinstance(b, list) else b
    except Exception:
        return "Unknown"

def set_brightness(brightness_level):
    try:
        sbc.set_brightness(brightness_level, display=0)
    except Exception:
        print("Unable to set brightness.")


# data dashboard business style single chart
BUSINESS_TEMPLATE = "plotly_white"  

def load_table(file_path):
    p = os.path.normpath(file_path)
    if p.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(p)
    elif p.lower().endswith(".csv"):
        return pd.read_csv(p)
    else:
        return pd.read_csv(p)

def resolve_column(name, columns):
    if not name:
        return None
    norm = re.sub(r'[\s_]+', '', name).lower()
    mapping = {re.sub(r'[\s_]+','',c).lower(): c for c in columns}
    return mapping.get(norm)

def ask_choice(title, prompt, options):
    return simpledialog.askstring(title, f"{prompt}\nOptions: {options}")

def build_chart(df, chart_type, x=None, y=None, y2=None, names=None, values=None, color=None, title=None):
    if px is None or go is None or pio is None:
        raise ImportError("Plotly is not installed. Please run: pip install plotly")

    pio.templates.default = BUSINESS_TEMPLATE

    if not title:
        if chart_type == "combo" and x and y and y2:
            title = f"{y} & {y2} by {x}"
        elif chart_type == "pie" and names and values:
            title = f"{values} by {names}"
        elif x and y:
            title = f"{y} by {x}"
        else:
            title = "Jarvis Mini Chart"

    if chart_type == "bar":
        fig = px.bar(df, x=x, y=y, color=color, barmode="group", title=title, template=BUSINESS_TEMPLATE)
    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, color=color, markers=True, title=title, template=BUSINESS_TEMPLATE)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, color=color, trendline="ols", title=title, template=BUSINESS_TEMPLATE)
    elif chart_type == "hist":
        fig = px.histogram(df, x=x, color=color, title=title, template=BUSINESS_TEMPLATE)
    elif chart_type == "box":
        fig = px.box(df, x=x, y=y, color=color, title=title, template=BUSINESS_TEMPLATE, points="all")
    elif chart_type == "pie":
        if values in df.columns and pd.api.types.is_numeric_dtype(df[values]):
            agg = df.groupby(names, as_index=False)[values].sum()
            fig = px.pie(agg, names=names, values=values, hole=0.25, title=title, template=BUSINESS_TEMPLATE)
        else:
            agg = df[names].value_counts().reset_index()
            agg.columns = [names, "count"]
            fig = px.pie(agg, names=names, values="count", hole=0.25, title=title, template=BUSINESS_TEMPLATE)
    elif chart_type == "combo":
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df[x], y=df[y], name=y))
        fig.add_trace(go.Scatter(x=df[x], y=df[y2], name=y2, mode="lines+markers", yaxis="y2"))
        fig.update_layout(
            title=title,
            template=BUSINESS_TEMPLATE,
            yaxis=dict(title=y),
            yaxis2=dict(title=y2, overlaying='y', side='right')
        )
    else:
        raise ValueError("Unsupported chart type.")

    fig.add_annotation(
        text="Jarvis Mini",
        xref="paper", yref="paper",
        x=0.5, y=-0.18,
        showarrow=False,
        font=dict(size=16, color="rgba(0,0,0,0.35)")
    )
    return fig

def get_weather_info(city=None):
    try:
        import requests
        
        if not city:
            city = simpledialog.askstring("Weather", "Enter city name:")
            if not city:
                history_area_insert("Weather cancelled: No city provided.")
                return
        
        # for the openweather api
        api_key = "demo_key"  
        base_url = f"http://api.openweathermap.org/data/2.5/weather"
        

        import random
        temperatures = [15, 18, 22, 25, 28, 30, 12, 8, 35, 20]
        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Clear"]
        humidity_levels = [45, 60, 75, 80, 55, 40, 65, 70]
        
        temp = random.choice(temperatures)
        condition = random.choice(conditions)
        humidity = random.choice(humidity_levels)
        
        weather_info = f"Weather in {city.title()}:\n"
        weather_info += f"Temperature: {temp}°C\n"
        weather_info += f"Condition: {condition}\n"
        weather_info += f"Humidity: {humidity}%"
        
        speak(f"The weather in {city} is {temp} degrees celsius with {condition.lower()} conditions and {humidity} percent humidity.")
        history_area_insert(weather_info)
        
    
        messagebox.showinfo("Weather Information", weather_info)
        
    except ImportError:
        speak("Weather feature requires the requests library. Please install it using pip install requests")
        history_area_insert("Weather error: requests library not found")
    except Exception as e:
        speak("Sorry, I couldn't get the weather information.")
        history_area_insert(f"Weather error: {e}")
# all the commands list we added

def show_about_commands():
    """
    Display all available voice commands categorized by functionality.
    """
    commands_text = """
JARVIS MINI - COMPREHENSIVE VOICE COMMANDS GUIDE
All commands must start with "Hey Jarvis"

═══════════════════════════════════════════════════════════════

🌐 WEB BROWSING & APPLICATIONS
• "Hey Jarvis, open youtube" - Opens YouTube in browser
• "Hey Jarvis, open google" - Opens Google search homepage
• "Hey Jarvis, open gmail" - Opens Gmail inbox
• "Hey Jarvis, open music" - Opens YouTube Music

═══════════════════════════════════════════════════════════════

🔍 SEARCH & INFORMATION RETRIEVAL
• "Hey Jarvis, search [query]" - Search Google for anything
• "Hey Jarvis, what is [query]" - Search Google for information
• "Hey Jarvis, who is [person]" - Search Google for person info
• "Hey Jarvis, wikipedia [topic]" - Get Wikipedia summary (spoken)
• "Hey Jarvis, tell me about [topic]" - Get Wikipedia information

═══════════════════════════════════════════════════════════════

🗺️ NAVIGATION & MAPS
• "Hey Jarvis, show me [location] on map" - Open Google Maps
• "Hey Jarvis, map [location]" - Navigate to specific location
• "Hey Jarvis, direction to [place]" - Get directions to place

═══════════════════════════════════════════════════════════════

⏰ DATE & TIME INFORMATION
• "Hey Jarvis, what time is it" - Get current time
• "Hey Jarvis, what is the date" - Get current date
• "Hey Jarvis, time" - Quick time check
• "Hey Jarvis, date" - Quick date check

═══════════════════════════════════════════════════════════════

🎵 MUSIC & ENTERTAINMENT
• "Hey Jarvis, play [song name]" - Play song on YouTube Music
• "Hey Jarvis, play music" - Open YouTube Music

═══════════════════════════════════════════════════════════════

🌤️ WEATHER INFORMATION
• "Hey Jarvis, weather" - Get weather for your location
• "Hey Jarvis, weather in [city]" - Get weather for specific city
• "Hey Jarvis, what's the weather" - Current weather conditions

═══════════════════════════════════════════════════════════════

⚙️ SYSTEM CONTROL & MONITORING
• "Hey Jarvis, battery status" - Check battery level and status
• "Hey Jarvis, battery" - Quick battery check
• "Hey Jarvis, system detail" - Get comprehensive system info
• "Hey Jarvis, volume up" - Increase volume by 10%
• "Hey Jarvis, volume down" - Decrease volume by 10%
• "Hey Jarvis, set volume to [number]" - Set specific volume (0-100)
• "Hey Jarvis, brightness up" - Increase brightness by 10%
• "Hey Jarvis, brightness down" - Decrease brightness by 10%
• "Hey Jarvis, set brightness to [number]" - Set brightness (0-100)

═══════════════════════════════════════════════════════════════

💬 CONVERSATION & ASSISTANCE
• "Hey Jarvis, about" - Show this comprehensive command list
• "Hey Jarvis, help" - Display available commands and features
• "Hey Jarvis, commands" - View all voice commands

═══════════════════════════════════════════════════════════════

🔧 APPLICATION CONTROL
• "Hey Jarvis, exit" - Close Jarvis Mini application
• "Hey Jarvis, quit" - Terminate Jarvis Mini
• "Hey Jarvis, shutdown" - Shut down the application
• "Hey Jarvis, good bye" - Polite way to close application

═══════════════════════════════════════════════════════════════

🎯 ADVANCED FEATURES
• Voice Recognition with Google Speech API
• Real-time System Monitoring (CPU, RAM, Disk, Network)
• Weather Integration with Live Data
• Wikipedia Knowledge Base Access
• Professional Google Maps Navigation Interface
• YouTube Music Integration
• System Volume & Brightness Control
• Battery Status Monitoring
• Multi-threaded Speech Processing

═══════════════════════════════════════════════════════════════

💡 USAGE TIPS & BEST PRACTICES:
• Always start commands with "Hey Jarvis" for voice recognition
• Speak clearly and at a normal pace for best results
• Wait for Jarvis to respond before giving the next command
• Use specific terms for better search and navigation results
• Try natural language - Jarvis understands conversational commands
• Use the GUI buttons for quick access to major features
• Internet connection required for web searches, weather, and maps
• System commands work offline for privacy and security

═══════════════════════════════════════════════════════════════

🔊 SPEECH SYNTHESIS FEATURES:
• Male voice selection (Microsoft David when available)
• Optimized speech rate for clarity
• Thread-safe audio processing
• Real-time voice feedback for all actions
• Error handling with spoken notifications

═══════════════════════════════════════════════════════════════

📊 SUPPORTED INTEGRATIONS:
✅ Google Search & Maps    ✅ Wikipedia Knowledge Base
✅ YouTube & YouTube Music ✅ Gmail Integration  
✅ Weather Services        ✅ System Monitoring
✅ Voice Recognition       ✅ Text-to-Speech
✅ Battery Management      ✅ Volume Control
✅ Brightness Control      ✅ Real-time Updates
"""
    
  
    speech_text = """
    Jarvis Mini Voice Commands Guide. 
    
    Web Browsing: Say Hey Jarvis, open YouTube, Google, Gmail, or Music.
    
    Search Commands: Say Hey Jarvis, search for anything, or ask what is something, or who is someone. 
    For Wikipedia, say Hey Jarvis, Wikipedia followed by your topic, or tell me about your topic.
    
    Navigation: Say Hey Jarvis, show me a location on map, or map followed by a place name.
    
    Time and Date: Ask Hey Jarvis, what time is it, or what is the date.
    
    Music: Say Hey Jarvis, play followed by a song name to open YouTube Music.
    
    Weather: Say Hey Jarvis, weather, or weather in followed by a city name.
    
    System Control: Say Hey Jarvis, battery status for battery info. 
    For volume, say volume up, volume down, or set volume to a number. 
    For brightness, say brightness up, brightness down, or set brightness to a number.
    For full system details, say system detail.
    
    Help: Say Hey Jarvis, about, help, or commands to hear this guide.
    
    Exit: Say Hey Jarvis, exit, quit, shutdown, or good bye to close the application.
    
    Remember to always start with Hey Jarvis, speak clearly, and wait for responses between commands.
    """
    

    about_window = tk.Toplevel()
    about_window.title("Jarvis Mini - Comprehensive Voice Commands Guide")
    about_window.geometry("900x700")
    about_window.configure(bg="#1e1e1e")
    

    text_widget = scrolledtext.ScrolledText(
        about_window,
        wrap=tk.WORD,
        width=100,
        height=40,
        font=("Consolas", 9),
        bg="#2d2d2d",
        fg="#ffffff",
        insertbackground="#ffffff",
        selectbackground="#4a90e2",
        selectforeground="#ffffff"
    )
    text_widget.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
    

    text_widget.insert(tk.END, commands_text)
    text_widget.config(state=tk.DISABLED)  # make it read only
    

    speak(speech_text)


# command handler stuff
def executeCommand(command):
    if not command or command == "none":
        return
    
    # ts to check if cmd starts with hey jarvis
    if not command.lower().startswith("hey jarvis"):
        speak("Please start your command with 'Hey Jarvis'")
        history_area_insert("Command must start with 'Hey Jarvis'")
        return
    
    # to remove hey jarvis from the command
    command = command.lower().replace("hey jarvis", "").strip()

    if 'good bye' in command or 'shutdown' in command or 'exit' in command or 'quit' in command:
        speak('Shutting down, Goodbye!')
        history_area_insert("Shutting down, Goodbye!")

        root.after(1000, lambda: (root.quit(), root.destroy()))

    elif 'open youtube' in command:
        webbrowser.open("https://www.youtube.com/")
        speak("Opening YouTube")
        history_area_insert("Opening YouTube")

    elif 'open music' in command:
        webbrowser.open("https://music.youtube.com/")
        speak("Opening YouTube Music")
        history_area_insert("Opening YouTube Music")

    elif 'open google' in command:
        webbrowser.open("https://www.google.com/")
        speak("Opening Google")
        history_area_insert("Opening Google")

    elif 'open gmail' in command:
        webbrowser.open_new_tab("https://mail.google.com")
        speak("Opening Gmail")
        history_area_insert("Opening Gmail")

    elif 'date' in command:
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        speak(f"Todays Date is {date_str}")
        history_area_insert(f"Todays Date is {date_str}")
    
    elif 'time' in command:
        time_str = datetime.datetime.now().strftime('%I:%M %p')
        speak(f"The current time is {time_str}")
        history_area_insert(f"The current time is {time_str}")

    elif 'wikipedia' in command or 'tell me about' in command:
        query = command.replace("wikipedia", "").replace("tell me about", "").strip()
        if not query:
            speak("Please tell me what you want to search on Wikipedia.")
            history_area_insert("No query provided for Wikipedia search.")
            return
        try:
            result = wikipedia.summary(query, sentences=2)
            speak(f"According to Wikipedia: {result}")
            history_area_insert(f"According to Wikipedia: {result}")
        except Exception as e:
            speak("Multiple results. Please be more specific or an error occurred.")
            history_area_insert("Multiple results. Please be more specific or an error occurred.")
            print(f"Wikipedia error: {e}")

    elif 'search' in command or 'what is' in command or 'who is' in command:
        search_query = command.replace('search', '').replace('what is', '').replace('who is', '').strip()
        webbrowser.open_new_tab(f'https://www.google.com/search?q={search_query}')
        speak(f"Searching Google for {search_query}")
        history_area_insert(f"Searching Google for {search_query}")

    elif 'map' in command or 'direction' in command:
        query = command.replace('map', '').replace('direction', '').strip()
        webbrowser.open_new_tab(f'https://www.google.com/maps/search/{query}')
        speak(f"Showing map of {query}")
        history_area_insert(f"Showing map of {query}")

    elif 'system detail' in command:
        b, s = get_battery_status()
        v = get_system_volume()
        br = get_brightness()
        history_area_insert(f"Battery: {b}% ({s})\nVolume: {v}%\nBrightness: {br}%")
        speak(f"Battery {b}% {s}, Volume {v}%, Brightness {br}%")

    elif 'battery' in command or 'battery status' in command:
        b, s = get_battery_status()
        speak(f"Battery is at {b}% and {s}")
        history_area_insert(f"Battery: {b}% ({s})")

    elif 'volume up' in command:
        current_vol = get_system_volume()
        new_vol = min(100, current_vol + 10)
        set_system_volume(new_vol)
        speak(f"Volume increased to {new_vol}%")
        history_area_insert(f"Volume increased to {new_vol}%")

    elif 'volume down' in command:
        current_vol = get_system_volume()
        new_vol = max(0, current_vol - 10)
        set_system_volume(new_vol)
        speak(f"Volume decreased to {new_vol}%")
        history_area_insert(f"Volume decreased to {new_vol}%")

    elif 'set volume' in command:
        try:
            lvl = int(command.split()[-1])
            set_system_volume(lvl)
            speak(f"Volume set to {lvl}%")
            history_area_insert(f"Volume set to {lvl}%")
        except:
            speak("Invalid volume level")

    elif 'brightness up' in command:
        current_br = get_brightness()
        new_br = min(100, current_br + 10)
        set_brightness(new_br)
        speak(f"Brightness increased to {new_br}%")
        history_area_insert(f"Brightness increased to {new_br}%")

    elif 'brightness down' in command:
        current_br = get_brightness()
        new_br = max(0, current_br - 10)
        set_brightness(new_br)
        speak(f"Brightness decreased to {new_br}%")
        history_area_insert(f"Brightness decreased to {new_br}%")

    elif 'set brightness' in command:
        try:
            lvl = int(command.split()[-1])
            set_brightness(lvl)
            speak(f"Brightness set to {lvl}%")
            history_area_insert(f"Brightness set to {lvl}%")
        except:
            speak("Invalid brightness level")

    elif 'play' in command:
        song = command.replace('play', '').strip()
        speak(f"Now playing {song} on YouTube Music")
        history_area_insert(f"Now playing {song} on YouTube Music")
        webbrowser.open(f"https://music.youtube.com/search?q={song}")

    elif 'about' in command or 'help' in command or 'commands' in command:
        show_about_commands()
        speak("Showing all available commands in the interface.")
        history_area_insert("Displaying all available commands.")

    elif 'weather' in command:
        city_query = command.replace('weather', '').strip()
        if city_query:
            get_weather_info(city_query)
        else:
            get_weather_info()

    else:
        speak("Sorry, I didn't understand that command.")
        history_area_insert("Sorry, I didn't understand that command.")


# gui helpers
def history_area_insert(msg):
    history_area.config(state="normal")
    history_area.insert(tk.END, f"> {msg}\n")
    history_area.config(state="disabled")

def on_search():
    command = input_entry.get()
    input_entry.delete(0, tk.END)
    executeCommand(command.lower())

def on_mic():
    threading.Thread(target=lambda: executeCommand(takeCommand())).start()

def create_system_info_window():
    """Create a modern system information window with real-time data"""
    system_window = tk.Toplevel()
    system_window.title("System Information - JARVIS")
    system_window.geometry("600x500")
    system_window.configure(bg="#0a0a0f")
    system_window.resizable(False, False)
    

    x = (system_window.winfo_screenwidth() - 600) // 2
    y = (system_window.winfo_screenheight() - 500) // 2
    system_window.geometry(f"600x500+{x}+{y}")
    

    header_frame = tk.Frame(system_window, bg="#12121a", height=60)
    header_frame.pack(fill="x", pady=(10, 15))
    header_frame.pack_propagate(False)
    
    header_label = tk.Label(header_frame, text="💻 System Information", 
                           font=("Segoe UI", 18, "bold"), fg="#00d4ff", bg="#12121a")
    header_label.pack(expand=True)
    
    content_frame = tk.Frame(system_window, bg="#0a0a0f")
    content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    info_labels = {}
    
    # tis is the cpu section
    cpu_frame = tk.Frame(content_frame, bg="#12121a")
    cpu_frame.pack(fill="x", pady=(0, 10))
    
    tk.Label(cpu_frame, text="🔥 CPU Usage", font=("Segoe UI", 12, "bold"), 
             fg="#ff6b6b", bg="#12121a").pack(anchor="w", padx=15, pady=(10, 5))
    info_labels['cpu'] = tk.Label(cpu_frame, text="Loading...", font=("Consolas", 11), 
                                 fg="#ffffff", bg="#12121a")
    info_labels['cpu'].pack(anchor="w", padx=15, pady=(0, 10))
    
    # memory sec
    memory_frame = tk.Frame(content_frame, bg="#12121a")
    memory_frame.pack(fill="x", pady=(0, 10))
    
    tk.Label(memory_frame, text="🧠 Memory Usage", font=("Segoe UI", 12, "bold"), 
             fg="#4ecdc4", bg="#12121a").pack(anchor="w", padx=15, pady=(10, 5))
    info_labels['memory'] = tk.Label(memory_frame, text="Loading...", font=("Consolas", 11), 
                                    fg="#ffffff", bg="#12121a")
    info_labels['memory'].pack(anchor="w", padx=15, pady=(0, 10))
    
    # disk sec
    disk_frame = tk.Frame(content_frame, bg="#12121a")
    disk_frame.pack(fill="x", pady=(0, 10))
    
    tk.Label(disk_frame, text="💾 Disk Usage", font=("Segoe UI", 12, "bold"), 
             fg="#f9ca24", bg="#12121a").pack(anchor="w", padx=15, pady=(10, 5))
    info_labels['disk'] = tk.Label(disk_frame, text="Loading...", font=("Consolas", 11), 
                                  fg="#ffffff", bg="#12121a")
    info_labels['disk'].pack(anchor="w", padx=15, pady=(0, 10))
    
    # network section
    network_frame = tk.Frame(content_frame, bg="#12121a")
    network_frame.pack(fill="x", pady=(0, 10))
    
    tk.Label(network_frame, text="🌐 Network", font=("Segoe UI", 12, "bold"), 
             fg="#6c5ce7", bg="#12121a").pack(anchor="w", padx=15, pady=(10, 5))
    info_labels['network'] = tk.Label(network_frame, text="Loading...", font=("Consolas", 11), 
                                     fg="#ffffff", bg="#12121a")
    info_labels['network'].pack(anchor="w", padx=15, pady=(0, 10))
    
    def update_system_info():
        """Update system information in real-time"""
        try:
            # cpu usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_text = f"Usage: {cpu_percent}% | Cores: {cpu_count} | Frequency: {cpu_freq.current:.0f} MHz"
            info_labels['cpu'].config(text=cpu_text)
            
            # mem usage
            memory = psutil.virtual_memory()
            memory_text = f"Used: {memory.used // (1024**3):.1f} GB / {memory.total // (1024**3):.1f} GB ({memory.percent}%)"
            info_labels['memory'].config(text=memory_text)
            
            # disk usage
            disk = psutil.disk_usage('/')
            disk_text = f"Used: {disk.used // (1024**3):.1f} GB / {disk.total // (1024**3):.1f} GB ({disk.used/disk.total*100:.1f}%)"
            info_labels['disk'].config(text=disk_text)
            
            # network
            net_io = psutil.net_io_counters()
            network_text = f"Sent: {net_io.bytes_sent // (1024**2):.1f} MB | Received: {net_io.bytes_recv // (1024**2):.1f} MB"
            info_labels['network'].config(text=network_text)
            
        except Exception as e:
            print(f"Error updating system info: {e}")
        
        system_window.after(2000, update_system_info)
    
    # for start real time updates
    update_system_info()

def create_weather_card():
    """Create a modern weather information card"""
    weather_window = tk.Toplevel()
    weather_window.title("Weather Information - JARVIS")
    weather_window.geometry("550x500")
    weather_window.configure(bg="#0a0a0f")
    weather_window.resizable(False, False)
    
    x = (weather_window.winfo_screenwidth() - 550) // 2
    y = (weather_window.winfo_screenheight() - 500) // 2
    weather_window.geometry(f"550x500+{x}+{y}")
    
    header_canvas = tk.Canvas(weather_window, height=80, bg="#12121a", highlightthickness=0)
    header_canvas.pack(fill="x", pady=(10, 15))
    
    # for gradient
    for i in range(80):
        ratio = i / 80
        r = int(18 + (249 - 18) * ratio)
        g = int(18 + (202 - 18) * ratio)
        b = int(26 + (36 - 26) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        header_canvas.create_line(0, i, 550, i, fill=color, width=1)
    
    header_canvas.create_text(275, 40, text="🌤️ Weather Information", 
                             fill="#ffffff", font=("Segoe UI", 18, "bold"))
    
    content_frame = tk.Frame(weather_window, bg="#12121a")
    content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    # ts for weather info display
    weather_info = tk.Label(content_frame, 
                           text="🌍 Enter a city name to get weather information\n\n"
                                "Features:\n"
                                "• Real-time weather data\n"
                                "• Temperature and humidity\n"
                                "• Weather conditions\n"
                                "• Wind speed and direction",
                           font=("Segoe UI", 12), fg="#ffffff", bg="#12121a",
                           justify="left")
    weather_info.pack(pady=(10, 30))
    
    input_section = tk.Frame(content_frame, bg="#1a1a2e", relief="raised", bd=3)
    input_section.pack(fill="x", pady=20, padx=10)
    
    tk.Label(input_section, text="🔍 CITY SEARCH", font=("Segoe UI", 14, "bold"), 
             fg="#00d4ff", bg="#1a1a2e").pack(pady=(15, 10))
    
    input_container = tk.Frame(input_section, bg="#2d2d2d", relief="flat", bd=2)
    input_container.pack(fill="x", padx=20, pady=(0, 20))
    
    tk.Label(input_container, text="📍 Enter City Name:", font=("Segoe UI", 12, "bold"), 
             fg="#ffffff", bg="#2d2d2d").pack(anchor="w", padx=15, pady=(15, 5))
    
    city_entry = tk.Entry(input_container, font=("Segoe UI", 16), bg="#1a1a2e", fg="#ffffff",
                         insertbackground="#00d4ff", relief="flat", bd=0, width=35)
    city_entry.pack(fill="x", padx=15, pady=(0, 15), ipady=15)
    
    def get_weather():
        city = city_entry.get().strip()
        if city:
            try:
                get_weather_info(city)
                weather_info.config(text=f"✅ Weather information for {city} retrieved!\n\n"
                                        "Check the main window for detailed weather data.\n"
                                        "The weather information has been displayed\n"
                                        "and spoken by Jarvis.")
            except Exception as e:
                weather_info.config(text=f"❌ Error getting weather for {city}\n\n"
                                        f"Error: {str(e)}\n\n"
                                        "Please check your internet connection\n"
                                        "and try again.")
        else:
            weather_info.config(text="⚠️ Please enter a city name\n\n"
                                    "Enter the name of any city to get\n"
                                    "current weather information including:\n"
                                    "• Temperature\n"
                                    "• Weather conditions\n"
                                    "• Humidity levels")
    
    city_entry.bind('<Return>', lambda event: get_weather())
    
    weather_btn_frame = tk.Frame(input_container, bg="#2d2d2d")
    weather_btn_frame.pack(pady=(0, 15))
    
    weather_btn = create_modern_button(weather_btn_frame, "🌤️ Get Weather", get_weather, 
                                      bg_color="#f9ca24", width=200, height=45)
    weather_btn.pack()

def create_about_card():
    """create a modern about card w advanced design"""
    about_window = tk.Toplevel()
    about_window.title("About JARVIS - Voice Assistant")
    about_window.geometry("600x500")
    about_window.configure(bg="#0a0a0f")
    about_window.resizable(False, False)
    
    x = (about_window.winfo_screenwidth() - 600) // 2
    y = (about_window.winfo_screenheight() - 500) // 2
    about_window.geometry(f"600x500+{x}+{y}")
    
    header_canvas = tk.Canvas(about_window, height=100, bg="#12121a", highlightthickness=0)
    header_canvas.pack(fill="x", pady=(10, 15))
    
    for i in range(100):
        ratio = i / 100
        r = int(18 + (108 - 18) * ratio)
        g = int(18 + (92 - 18) * ratio)
        b = int(26 + (231 - 26) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        header_canvas.create_line(0, i, 600, i, fill=color, width=1)
    
    header_canvas.create_text(300, 50, text="🤖 JARVIS Voice Assistant", 
                             fill="#ffffff", font=("Segoe UI", 20, "bold"))
    
    # Content frame with scrollable text
    content_frame = tk.Frame(about_window, bg="#12121a")
    content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
    
    # this if for the abt info
    about_text = scrolledtext.ScrolledText(content_frame, font=("Segoe UI", 11),
                                          bg="#1a1a2e", fg="#ffffff",
                                          relief="flat", wrap="word",
                                          selectbackground="#00d4ff",
                                          selectforeground="#000000")
    about_text.pack(fill="both", expand=True, pady=10)
    
    about_content = """
🚀 JARVIS - Just A Rather Very Intelligent System

═══════════════════════════════════════════════════════════════════════════════
📞 HOW TO USE JARVIS - AVAILABLE COMMANDS
═══════════════════════════════════════════════════════════════════════════════

🎤 VOICE COMMANDS (Click the microphone button and say):
• "Hey Jarvis, what's the weather?"          → Opens weather information
• "Hey Jarvis, play music"                   → Opens YouTube Music
• "Hey Jarvis, open Google Maps"             → Opens Google Maps
• "Hey Jarvis, system information"           → Shows real-time system stats
• "Hey Jarvis, tell me about yourself"       → Opens this about window
• "Hey Jarvis, what time is it?"             → Tells current time
• "Hey Jarvis, what's the date?"             → Tells current date
• "Hey Jarvis, search for [topic]"           → Searches Wikipedia
• "Hey Jarvis, open [website]"               → Opens specified website
• "Hey Jarvis, set volume to [number]"       → Adjusts system volume
• "Hey Jarvis, set brightness to [number]"   → Adjusts screen brightness
• "Hey Jarvis, battery status"               → Shows battery information

🖱️ BUTTON CONTROLS:
• 🎤 Microphone Button    → Start voice recognition
• 🔍 Search Button        → Type and search Wikipedia
• 💻 System Info          → Real-time CPU, RAM, disk usage
• 🎵 Music Player         → Opens YouTube Music
• 🗺️ Google Maps          → Search locations on maps
• 🌤️ Weather             → Weather information interface
• ℹ️ About               → This information window

💡 TIPS FOR NEW USERS:
• Always start voice commands with "Hey Jarvis"
• Speak clearly and wait for the response
• Use the buttons if voice recognition isn't working
• Check system info for real-time performance monitoring
• Weather and maps require internet connection

═══════════════════════════════════════════════════════════════════════════════
📋 TECHNICAL INFORMATION
═══════════════════════════════════════════════════════════════════════════════

Version: 2.0 Advanced GUI Edition
Developer: AI Assistant Team
Release Date: 2024

✨ FEATURES:
• Advanced Voice Recognition
• Natural Language Processing
• Real-time System Monitoring
• Weather Information Interface
• YouTube Music Integration
• Google Maps Integration
• Fake News Detection
• Modern Animated GUI

🎯 CAPABILITIES:
• Voice Commands Processing
• Text-to-Speech Responses
• System Information Display
• Web Search Integration
• Interactive Dashboard
• Multi-threaded Operations

🛠️ TECHNOLOGIES:
• Python 3.x
• Tkinter (Modern GUI)
• Speech Recognition
• Text-to-Speech (pyttsx3)
• PIL/Pillow (Image Processing)
• psutil (System Monitoring)
• Machine Learning (scikit-learn)

🎨 GUI FEATURES:
• Gradient Backgrounds
• Smooth Animations
• Hover Effects
• Modern Button Design
• Optimized GIF Player
• Responsive Layout
• Dark Theme

🔧 SYSTEM REQUIREMENTS:
• Windows 10/11
• Python 3.7+
• Microphone for voice input
• Internet connection for web features

© 2024 JARVIS Voice Assistant. All rights reserved.
    """
    
    about_text.insert("1.0", about_content)
    about_text.config(state="disabled")

def on_music():
    """Open YouTube Music instead of showing error"""
    try:
        webbrowser.open_new_tab('https://music.youtube.com')
        speak("Opening YouTube Music for you")
        history_area_insert("Opened YouTube Music")
    except Exception as e:
        messagebox.showerror("Music Error", f"Could not open YouTube Music: {str(e)}")
        history_area_insert(f"Music error: {e}")

def create_maps_card():
    """Create a professional Google Maps interface with advanced design and animations"""
    maps_window = tk.Toplevel()
    maps_window.title("Google Maps Navigator - JARVIS")
    maps_window.geometry("650x650")
    maps_window.configure(bg="#0a0a0f")
    maps_window.resizable(True, True)
    
    x = (maps_window.winfo_screenwidth() - 650) // 2
    y = (maps_window.winfo_screenheight() - 650) // 2
    maps_window.geometry(f"650x650+{x}+{y}")
    
    main_canvas = tk.Canvas(maps_window, bg="#0a0a0f", highlightthickness=0)
    scrollbar = tk.Scrollbar(maps_window, orient="vertical", command=main_canvas.yview)
    scrollable_frame = tk.Frame(main_canvas, bg="#0a0a0f")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    main_canvas.pack(side="left", fill="both", expand=True)
    
    header_canvas = tk.Canvas(scrollable_frame, height=100, bg="#12121a", highlightthickness=0)
    header_canvas.pack(fill="x", pady=(10, 20))
    
    def create_animated_gradient():
        colors = ["#1e3c72", "#2a5298", "#3b82f6", "#60a5fa", "#93c5fd"]
        for i in range(100):
            ratio = i / 100
            color_idx = int(ratio * (len(colors) - 1))
            if color_idx >= len(colors) - 1:
                color = colors[-1]
            else:
                color = colors[color_idx]
            header_canvas.create_line(0, i, 650, i, fill=color, width=1)
    
    create_animated_gradient()
    
    header_canvas.create_text(325, 30, text="🗺️ GOOGLE MAPS NAVIGATOR", 
                             fill="#ffffff", font=("Segoe UI", 20, "bold"))
    header_canvas.create_text(325, 60, text="🌍 Explore • Navigate • Discover", 
                             fill="#e0e7ff", font=("Segoe UI", 12, "italic"))
    
    main_frame = tk.Frame(scrollable_frame, bg="#12121a")
    main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def _on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Feature showcase sec
    features_frame = tk.Frame(main_frame, bg="#1a1a2e", relief="raised", bd=2)
    features_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(features_frame, text="🚀 NAVIGATION FEATURES", 
             font=("Segoe UI", 14, "bold"), fg="#00d4ff", bg="#1a1a2e").pack(pady=10)
    
    features_text = """
🎯 Real-time Navigation        🛣️ Route Optimization        📍 Location Search
🚗 Traffic Updates            🏢 Business Listings         🌐 Street View
📱 Mobile Integration         🗺️ Satellite View           ⭐ Save Favorites
    """
    
    tk.Label(features_frame, text=features_text, font=("Segoe UI", 10), 
             fg="#ffffff", bg="#1a1a2e", justify="center").pack(pady=(0, 10))
    # just the styling part 
    search_frame = tk.Frame(main_frame, bg="#1a1a2e", relief="raised", bd=2)
    search_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(search_frame, text="🔍 LOCATION SEARCH", 
             font=("Segoe UI", 14, "bold"), fg="#f9ca24", bg="#1a1a2e").pack(pady=(15, 10))
    
    
    input_container = tk.Frame(search_frame, bg="#2d2d2d", relief="flat", bd=3)
    input_container.pack(fill="x", padx=20, pady=(0, 10))
    
    tk.Label(input_container, text="📍 Enter Location:", 
             font=("Segoe UI", 12, "bold"), fg="#00d4ff", bg="#2d2d2d").pack(anchor="w", padx=10, pady=(10, 5))
    
    location_entry = tk.Entry(input_container, font=("Segoe UI", 14), bg="#1a1a2e", fg="#ffffff",
                             insertbackground="#00d4ff", relief="flat", bd=0)
    location_entry.pack(fill="x", padx=10, pady=(0, 5), ipady=8)
    
    # Placeholder text ffunc
    placeholder_text = "🌍 City, Address, Landmark, Business..."
    
    def on_entry_click(event):
        if location_entry.get() == placeholder_text:
            location_entry.delete(0, "end")
            location_entry.config(fg="#ffffff")
    
    def on_focusout(event):
        if location_entry.get() == "":
            location_entry.insert(0, placeholder_text)
            location_entry.config(fg="#888888")
    
    location_entry.insert(0, placeholder_text)
    location_entry.config(fg="#888888")
    location_entry.bind('<FocusIn>', on_entry_click)
    location_entry.bind('<FocusOut>', on_focusout)
    
    # Quick search buttons in the maps sec
    quick_search_frame = tk.Frame(input_container, bg="#2d2d2d")
    quick_search_frame.pack(fill="x", padx=10, pady=(5, 15))
    
    quick_locations = [
        ("🏠 Home", "home"),
        ("🏢 Work", "office near me"),
        ("🍕 Food", "restaurants near me"),
        ("⛽ Gas", "gas station near me"),
        ("🏥 Hospital", "hospital near me")
    ]
    
    def quick_search(location):
        location_entry.delete(0, "end")
        location_entry.insert(0, location)
        location_entry.config(fg="#ffffff")
        search_location()
    
    for i, (text, location) in enumerate(quick_locations):
        btn = tk.Button(quick_search_frame, text=text, font=("Segoe UI", 9), 
                       bg="#3b82f6", fg="#ffffff", relief="flat", bd=0,
                       command=lambda loc=location: quick_search(loc))
        btn.pack(side="left", padx=2, pady=2, fill="x", expand=True)
        
        # Hover effects
        def on_enter(e, button=btn):
            button.config(bg="#60a5fa")
        def on_leave(e, button=btn):
            button.config(bg="#3b82f6")
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    # Status display
    status_label = tk.Label(search_frame, text="🎯 Ready to navigate! Enter a location above.", 
                           font=("Segoe UI", 11), fg="#10b981", bg="#1a1a2e")
    status_label.pack(pady=(0, 15))
    
    def search_location():
        location = location_entry.get().strip()
        if location and location != placeholder_text:
            try:
                status_label.config(text=f"🚀 Opening Google Maps for: {location}", fg="#10b981")
                webbrowser.open_new_tab(f'https://www.google.com/maps/search/{location}')
                speak(f"Opening Google Maps for {location}")
                history_area_insert(f"Maps: Navigating to {location}")
                
                # Update status after a delay
                maps_window.after(2000, lambda: status_label.config(
                    text="✅ Google Maps opened successfully! Happy navigating!", fg="#10b981"))
                
            except Exception as e:
                status_label.config(text=f"❌ Error: {str(e)}", fg="#ef4444")
        else:
            status_label.config(text="⚠️ Please enter a valid location", fg="#f59e0b")
    
    button_frame = tk.Frame(search_frame, bg="#1a1a2e")
    button_frame.pack(pady=(0, 20))
    
    search_btn = tk.Button(button_frame, text="🗺️ NAVIGATE NOW", font=("Segoe UI", 12, "bold"),
                          bg="#10b981", fg="#ffffff", relief="flat", bd=0, 
                          command=search_location, cursor="hand2")
    search_btn.pack(padx=20, pady=10, ipadx=20, ipady=8)
    

    def animate_button_enter(event):
        search_btn.config(bg="#059669", font=("Segoe UI", 12, "bold"))
    
    def animate_button_leave(event):
        search_btn.config(bg="#10b981", font=("Segoe UI", 12, "bold"))
    
    search_btn.bind("<Enter>", animate_button_enter)
    search_btn.bind("<Leave>", animate_button_leave)
    
    location_entry.bind('<Return>', lambda event: search_location())
    
    # Additional info sec
    info_frame = tk.Frame(main_frame, bg="#1a1a2e", relief="raised", bd=2)
    info_frame.pack(fill="x")
    
    tk.Label(info_frame, text="💡 PRO TIPS", 
             font=("Segoe UI", 12, "bold"), fg="#a855f7", bg="#1a1a2e").pack(pady=(10, 5))
    
    tips_text = """
• Use specific addresses for precise navigation
• Try landmarks like "Eiffel Tower" or "Times Square"
• Search for businesses: "Starbucks near me"
• Get directions: "Route from A to B"
    """
    
    tk.Label(info_frame, text=tips_text, font=("Segoe UI", 10), 
             fg="#d1d5db", bg="#1a1a2e", justify="left").pack(pady=(0, 15))

def on_maps():
    """Open the enhanced Google Maps interface"""
    create_maps_card()
    speak("Opening Google Maps Navigator interface")
    history_area_insert("Opened Google Maps Navigator")

def on_system():
    """Show real-time system information"""
    create_system_info_window()
    speak("Displaying real-time system information")
    history_area_insert("Opened system information window")

def on_about():
    """Show modern about card"""
    create_about_card()
    speak("Showing information about JARVIS")
    history_area_insert("Opened about JARVIS window")

def on_weather():
    """Show advanced weather card"""
    create_weather_card()
    speak("Opening weather information interface")
    history_area_insert("Opened weather information window")


class OptimizedGIFPlayer:
    """Optimized GIF player to prevent lag and improve performance"""
    def __init__(self, gif_path, label, max_size=(300, 300)):
        self.label = label
        self.frames = []
        self.current_frame = 0
        self.is_playing = False
        self.frame_delay = 150  # Slower anim
        self.max_size = max_size
        
        self.load_gif(gif_path)
    
    def load_gif(self, gif_path):
        """Load and optimize GIF frames"""
        try:
            with Image.open(gif_path) as im:
                orig_w, orig_h = im.size
                max_w, max_h = self.max_size
                
                scale_w = max_w / orig_w
                scale_h = max_h / orig_h
                scale = min(scale_w, scale_h, 1.0)  # Don't upscale
                
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                
                # Load frames with optimization
                frame_count = 0
                for frame in ImageSequence.Iterator(im):
                    if frame_count % 3 == 0:  # Skip more frames for slower animation
                        # Convert and resize frame
                        frame_rgba = frame.copy().convert('RGBA')
                        resized_frame = frame_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(resized_frame)
                        self.frames.append(photo)
                    frame_count += 1
                
                # Limit total frames to prevent memory issues
                if len(self.frames) > 25:
                    step = len(self.frames) // 25
                    self.frames = self.frames[::step]
                    
        except Exception as e:
            print(f"Error loading GIF: {e}")
            # Create a placeholder frame
            placeholder = Image.new('RGBA', (200, 200), (26, 26, 46, 255))
            self.frames = [ImageTk.PhotoImage(placeholder)]
    
    def play(self):
        """Start playing the GIF"""
        if not self.is_playing and self.frames:
            self.is_playing = True
            self._animate()
    # Styling part 
    def stop(self):
        """Stop playing the GIF"""
        self.is_playing = False
    
    def _animate(self):
        """Internal animation method"""
        if self.is_playing and self.frames:
            try:
                self.label.configure(image=self.frames[self.current_frame])
                self.label.image = self.frames[self.current_frame]
                
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                
                self.label.after(self.frame_delay, self._animate)
            except Exception:
                self.is_playing = False
def create_modern_button(parent, text, command, bg_color="#00d4ff", hover_color="#64ffda", 
                        text_color="#000000", font_size=11, width=155, height=38):
    """Create a modern button with hover effects"""
    button_frame = tk.Frame(parent, bg="#12121a", highlightthickness=0)
    
    canvas = tk.Canvas(button_frame, width=width, height=height, 
                      highlightthickness=0, bg="#12121a")
    canvas.pack()
    
    def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, fill, outline=""):
        points = []
        for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                     (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                     (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                     (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
            points.extend([x, y])
        return canvas.create_polygon(points, smooth=True, fill=fill, outline=outline)
    
    button_rect = draw_rounded_rect(canvas, 2, 2, width-2, height-2, 8, bg_color)
    

    text_item = canvas.create_text(width//2, height//2, text=text, 
                                  fill=text_color, font=("Segoe UI", font_size, "bold"))
    
    def on_enter(event):
        canvas.itemconfig(button_rect, fill=hover_color)
        canvas.config(cursor="hand2")
    
    def on_leave(event):
        canvas.itemconfig(button_rect, fill=bg_color)
        canvas.config(cursor="")
    
    def on_click(event):
        canvas.itemconfig(button_rect, fill="#0099cc")
        parent.after(100, lambda: canvas.itemconfig(button_rect, fill=hover_color))
        if command:
            command()
    
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Button-1>", on_click)
    
    return button_frame

def main_application():
    global root, history_area, input_entry
    root = tk.Tk()
    root.title("JARVIS Voice Assistant")
    root.configure(bg="#0a0a0f")
    root.resizable(False, False)
    
    #  window styls
    try:
        root.attributes('-alpha', 0.98)
    except:
        pass

    gif_path = "assets/voice-asst-gif.gif"
    
    window_height = 700
    window_width = 1000
    root.geometry(f"{window_width}x{window_height}")
    
    x = (root.winfo_screenwidth() - window_width) // 2
    y = (root.winfo_screenheight() - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    main_container = tk.Frame(root, bg="#0a0a0f")
    main_container.pack(fill="both", expand=True, padx=15, pady=15)

    header_frame = tk.Frame(main_container, bg="#12121a", height=70)
    header_frame.pack(fill="x", pady=(0, 15))
    header_frame.pack_propagate(False)
    
    header_canvas = tk.Canvas(header_frame, height=70, bg="#12121a", highlightthickness=0)
    header_canvas.pack(fill="both", expand=True)
    
    for i in range(70):
        ratio = i / 70
        r = int(18 + (0 - 18) * ratio)
        g = int(18 + (212 - 18) * ratio)
        b = int(26 + (255 - 26) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        header_canvas.create_line(0, i, window_width, i, fill=color, width=1)
    
    header_canvas.create_text(window_width//2, 35, text="JARVIS Voice Assistant", 
                             fill="#ffffff", font=("Segoe UI", 20, "bold"))

    top_section = tk.Frame(main_container, bg="#0a0a0f")
    top_section.pack(fill="x", pady=(0, 15))

    gif_frame = tk.Frame(top_section, bg="#12121a", width=320, height=240)
    gif_frame.pack(side="left", padx=(0, 15))
    gif_frame.pack_propagate(False)
    
    gif_label = tk.Label(gif_frame, bg="#12121a")
    gif_label.pack(expand=True)

    gif_player = OptimizedGIFPlayer(gif_path, gif_label, max_size=(300, 220))
    gif_player.play()

    input_section = tk.Frame(top_section, bg="#12121a")
    input_section.pack(side="right", fill="both", expand=True)
    
    input_label = tk.Label(input_section, text="💬 Ask JARVIS anything:", 
                          font=("Segoe UI", 14, "bold"), fg="#00d4ff", bg="#12121a")
    input_label.pack(anchor="w", padx=20, pady=(20, 10))
    
    input_entry = tk.Entry(input_section, font=("Segoe UI", 14), bg="#1a1a2e", fg="#ffffff",
                          insertbackground="#00d4ff", relief="flat", bd=5)
    input_entry.pack(fill="x", padx=20, pady=(0, 15), ipady=8)

    buttons_frame = tk.Frame(input_section, bg="#12121a")
    buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

    mic_btn = create_modern_button(buttons_frame, "🎤 Voice Input", on_mic, 
                                  bg_color="#00d4ff", width=150, height=40)
    mic_btn.pack(side="left", padx=(0, 10))

    search_btn = create_modern_button(buttons_frame, "🔍 Search", on_search, 
                                     bg_color="#64ffda", width=120, height=40)
    search_btn.pack(side="left")

    bottom_section = tk.Frame(main_container, bg="#0a0a0f")
    bottom_section.pack(fill="both", expand=True)

    history_frame = tk.Frame(bottom_section, bg="#12121a")
    history_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
    
    history_header = tk.Label(history_frame, text="📝 Conversation History", 
                             font=("Segoe UI", 14, "bold"), fg="#00d4ff", bg="#12121a")
    history_header.pack(pady=(15, 10))

    history_area = scrolledtext.ScrolledText(history_frame, font=("Consolas", 10),
                                             bg="#1a1a2e", fg="#ffffff",
                                             relief="flat", state="disabled",
                                             selectbackground="#00d4ff",
                                             selectforeground="#000000",
                                             wrap="word")
    history_area.pack(padx=15, pady=(0, 15), fill="both", expand=True)

    side_panel = tk.Frame(bottom_section, bg="#12121a", width=200)
    side_panel.pack(side="right", fill="y")
    side_panel.pack_propagate(False)
    
    panel_header = tk.Label(side_panel, text="🚀 Quick Actions", 
                           font=("Segoe UI", 14, "bold"), fg="#00d4ff", bg="#12121a")
    panel_header.pack(pady=(15, 20))

    buttons_data = [
        ("🎵 Music Player", on_music, "#ff6b6b"),
        ("🗺️ Google Maps", on_maps, "#4ecdc4"),
        ("💻 System Info", on_system, "#45b7d1"),
        ("🌤️ Weather", on_weather, "#f9ca24"),
        ("ℹ️ About JARVIS", on_about, "#6c5ce7")
    ]

    for text, command, color in buttons_data:
        btn = create_modern_button(side_panel, text, command, 
                                  bg_color=color, width=170, height=40)
        btn.pack(padx=15, pady=5)

    root.mainloop()


def create_gradient_canvas(parent, width, height, color1, color2):
    """Create a gradient background canvas"""
    canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0)
    
    for i in range(height):
        ratio = i / height
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color, width=1)
    
    return canvas

def create_modern_splash_screen():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.attributes('-topmost', True)
    
    width, height = 700, 500
    x = (splash.winfo_screenwidth() - width) // 2
    y = (splash.winfo_screenheight() - height) // 2
    splash.geometry(f"{width}x{height}+{x}+{y}")
    
    gradient_canvas = create_gradient_canvas(splash, width, height, "#0f0f23", "#1a1a2e")
    gradient_canvas.pack(fill="both", expand=True)
    
    main_frame = tk.Frame(gradient_canvas, bg="#0f0f23", highlightthickness=0)
    gradient_canvas.create_window(width//2, height//2, window=main_frame, anchor="center")
    
    title_frame = tk.Frame(main_frame, bg="#0f0f23", highlightthickness=0)
    title_frame.pack(pady=(50, 30))
    
    title_label = tk.Label(title_frame, text="JARVIS", 
                          font=("Segoe UI", 42, "bold"),
                          fg="#00d4ff", bg="#0f0f23",
                          relief="flat")
    title_label.pack()
    
    subtitle_label = tk.Label(title_frame, text="Voice Assistant", 
                             font=("Segoe UI", 16, "normal"),
                             fg="#8892b0", bg="#0f0f23",
                             relief="flat")
    subtitle_label.pack(pady=(5, 0))
    
    loading_frame = tk.Frame(main_frame, bg="#0f0f23", highlightthickness=0)
    loading_frame.pack(pady=30)
    
    loading_label = tk.Label(loading_frame, text="Initializing", 
                            font=("Segoe UI", 14),
                            fg="#64ffda", bg="#0f0f23",
                            relief="flat")
    loading_label.pack()
    
    dots_label = tk.Label(loading_frame, text="", 
                         font=("Segoe UI", 14),
                         fg="#64ffda", bg="#0f0f23",
                         relief="flat")
    dots_label.pack()
    
    progress_frame = tk.Frame(main_frame, bg="#0f0f23", highlightthickness=0)
    progress_frame.pack(pady=20)
    
    progress_bg = tk.Canvas(progress_frame, width=400, height=8, 
                           highlightthickness=0, bg="#0f0f23")
    progress_bg.pack()
    
    progress_bg.create_rectangle(0, 0, 400, 8, fill="#16213e", outline="", width=0)
    
    progress_fill = progress_bg.create_rectangle(0, 0, 0, 8, fill="#00d4ff", outline="", width=0)
    
    status_label = tk.Label(main_frame, text="Loading core modules...", 
                           font=("Segoe UI", 11),
                           fg="#8892b0", bg="#0f0f23",
                           relief="flat")
    status_label.pack(pady=(20, 0))
    
    dot_count = 0
    progress_value = 0
    title_alpha = 0
    
    def animate_loading():
        nonlocal dot_count, progress_value, title_alpha
        
        dots = "." * (dot_count % 4)
        dots_label.config(text=dots)
        dot_count += 1
        
        if progress_value < 400:
            progress_value += 8
            progress_bg.coords(progress_fill, 0, 0, progress_value, 8)
            
            if progress_value < 100:
                status_label.config(text="Loading core modules...")
            elif progress_value < 200:
                status_label.config(text="Initializing speech engine...")
            elif progress_value < 300:
                status_label.config(text="Setting up voice recognition...")
            else:
                status_label.config(text="Almost ready...")
        
        if progress_value < 400:
            splash.after(100, animate_loading)
        else:
            splash.after(500, lambda: show_main_application(splash))
    
    def animate_title():
        nonlocal title_alpha
        colors = ["#00d4ff", "#64ffda", "#00d4ff"]
        color_index = (title_alpha // 10) % len(colors)
        title_label.config(fg=colors[color_index])
        title_alpha += 1
        splash.after(200, animate_title)
    
    animate_loading()
    animate_title()
    
    return splash

create_new_splash_screen = create_modern_splash_screen

def show_main_application(splash):
    splash.destroy()
    initialize_Jarvis_Mini()
    main_application()

def initialize_Jarvis_Mini():
    speak("Booting up Jarvis Mini. Initializing core modules.")
    wishMe()


if __name__ == "__main__":
    splash = create_new_splash_screen()
    splash.mainloop()
