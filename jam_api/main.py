import requests
import sqlite3
import flet as ft
from datetime import datetime

def init_db():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region_id INTEGER,
            weather TEXT NOT NULL,
            recorded_at DATETIME NOT NULL,
            FOREIGN KEY (region_id) REFERENCES regions (id)
        )
    """)

    conn.commit()
    conn.close()

def extract_regions(data, region_list=None):
    if region_list is None:
        region_list = {}
    for key, value in data.items():
        if isinstance(value, dict):
            if "name" in value:
                region_list[key] = value["name"]
            else:
                extract_regions(value, region_list)
    return region_list

def fetch_area_list():
    area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
    try:
        response = requests.get(area_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"地域リスト取得エラー: {e}")
        return None

def fetch_weather_forecast(area_code):
    forecast_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"天気予報取得エラー: {e}")
        return None

def save_weather_to_db(area_code, region_name, weather):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO regions (area_code, name)
        VALUES (?, ?)
    """, (area_code, region_name))

    cursor.execute("SELECT id FROM regions WHERE area_code = ?", (area_code,))
    region_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO weather_data (region_id, weather, recorded_at)
        VALUES (?, ?, ?)
    """, (region_id, weather, datetime.now()))

    conn.commit()
    conn.close()

def get_weather_history():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.name, wd.weather, wd.recorded_at
        FROM weather_data wd
        JOIN regions r ON wd.region_id = r.id
        ORDER BY wd.recorded_at DESC
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def clear_weather_history():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM weather_data")
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.padding = 20

    area_dropdown = ft.Dropdown(label="地域を選択してください", options=[])
    sub_area_dropdown = ft.Dropdown(label="エリアを選択してください", options=[], disabled=True)
    forecast_output = ft.Text("", size=14, expand=True)
    history_output = ft.Text("", size=12, expand=True)
    fetch_button = ft.ElevatedButton("天気予報を取得", disabled=True)
    history_button = ft.ElevatedButton("履歴を表示")
    clear_history_button = ft.ElevatedButton("履歴を消去")
    area_list = {}
    sub_area_list = {}

    def load_area_list():
        nonlocal area_list
        area_data = fetch_area_list()
        if area_data:
            area_list = extract_regions(area_data)
            area_dropdown.options = [ft.dropdown.Option(text=name) for name in area_list.values()]
            fetch_button.disabled = False
        else:
            area_dropdown.options = [ft.dropdown.Option(text="地域リストを取得できませんでした")]
            fetch_button.disabled = True
        page.update()

    def area_selected(e):
        selected_area_name = area_dropdown.value
        selected_area_code = next((code for code, name in area_list.items() if name == selected_area_name), None)

        if not selected_area_code:
            sub_area_dropdown.options = []
            sub_area_dropdown.disabled = True
            page.update()
            return

        forecast_data = fetch_weather_forecast(selected_area_code)
        if forecast_data:
            nonlocal sub_area_list
            weather_areas = forecast_data[0]["timeSeries"][0]["areas"]
            sub_area_list = {area["area"]["name"]: area for area in weather_areas}
            sub_area_dropdown.options = [ft.dropdown.Option(text=name) for name in sub_area_list.keys()]
            sub_area_dropdown.disabled = False
        page.update()

    def fetch_forecast(e):
        selected_sub_area_name = sub_area_dropdown.value
        selected_area_code = next((code for code, name in area_list.items() if name == area_dropdown.value), None)

        if not selected_sub_area_name or not selected_area_code:
            forecast_output.value = "エリアが選択されていません。"
            page.update()
            return

        selected_sub_area = sub_area_list.get(selected_sub_area_name)
        weather_data = f"{selected_sub_area_name}: {selected_sub_area['weathers'][0]}"
        forecast_output.value = weather_data

        save_weather_to_db(selected_area_code, area_dropdown.value, selected_sub_area['weathers'][0])
        page.update()

    def show_weather_history(e):
        history = get_weather_history()
        history_output.value = "\n".join(
            [f"{name} | 天気: {weather} | 記録日時: {recorded_at}" for name, weather, recorded_at in history]
        )
        page.update()

    def clear_history(e):
        clear_weather_history()
        history_output.value = "履歴が消去されました。"
        page.update()

    page.add(
        ft.Column(
            [
                ft.Text("天気予報アプリ", size=24, weight="bold"),
                area_dropdown,
                sub_area_dropdown,
                fetch_button,
                forecast_output,
                ft.Divider(),
                history_button,
                clear_history_button,
                history_output,
            ],
            spacing=10,
            expand=True,
        )
    )

    area_dropdown.on_change = area_selected
    fetch_button.on_click = fetch_forecast
    history_button.on_click = show_weather_history
    clear_history_button.on_click = clear_history

    init_db()
    load_area_list()

if __name__ == "__main__":
    ft.app(target=main)
