import requests
import json
import flet as ft

# 地域リストを再帰的に取得する関数
def extract_regions(data, region_list=None):
    """
    再帰的にJSONデータを走査し、nameキーを持つ地域情報を抽出する関数。
    """
    if region_list is None:
        region_list = {}

    for key, value in data.items():
        if isinstance(value, dict):  # 辞書型であることを確認
            if "name" in value:  # nameキーがある場合
                region_list[key] = value["name"]
            else:
                # 再帰的に子要素を解析
                extract_regions(value, region_list)
    return region_list

# 地域リストを取得する関数
def fetch_area_list():
    """
    気象庁APIから地域リストを取得する関数。
    """
    area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
    try:
        response = requests.get(area_url)
        response.raise_for_status()  # HTTPエラーを例外として扱う
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"地域リスト取得エラー: {e}")
        return None

# 天気予報を取得する関数
def fetch_weather_forecast(area_code):
    """
    指定地域の天気予報を取得する関数。
    """
    forecast_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()  # HTTPエラーを例外として扱う
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"天気予報取得エラー: {e}")
        return None

# 天気データをフォーマットする関数
def format_weather(forecast_data):
    """
    天気データを整形して文字列として返す関数。
    """
    try:
        time_series = forecast_data[0]["timeSeries"][0]  # 時系列データを取得
        areas = time_series["areas"]
        result = []
        for area in areas:
            name = area["area"]["name"]
            weather = area["weathers"][0]
            result.append(f"{name}: {weather}")
            
        return "\n".join(result)
    except (KeyError, IndexError) as e:
        return f"データ解析エラー: {e}"

# Fletアプリケーション
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.padding = 20

    # UIコンポーネント
    area_dropdown = ft.Dropdown(label="地域を選択してください", options=[])
    forecast_output = ft.Text("", size=14, expand=True)
    fetch_button = ft.ElevatedButton("天気予報を取得", disabled=True)
    area_list = {}

    # 地域リストを取得し、Dropdownに反映
    def load_area_list():
        nonlocal area_list
        loading_text = ft.Text("地域リストを読み込んでいます...", size=16, weight="bold")
        page.add(loading_text)
        page.update()

        area_data = fetch_area_list()
        if area_data:
            try:
                # JSONデータを再帰的に解析して地域リストを抽出
                area_list = extract_regions(area_data)

                # 抽出結果をデバッグ出力
                # print("フィルタリングされた地域リスト:")
                # print(json.dumps(area_list, indent=4, ensure_ascii=False))
                print(area_data)

                # Dropdownオプションを設定
                area_dropdown.options = [
                    ft.dropdown.Option(text=name) for code, name in area_list.items()
                ]
                fetch_button.disabled = False
            except Exception as e:
                print(f"地域リスト解析エラー: {e}")
                area_list = {}  # エラー時は空の辞書を設定
                fetch_button.disabled = True

        else:
            area_dropdown.options = [
                ft.dropdown.Option(text="地域リストを取得できませんでした")
            ]
            fetch_button.disabled = True

        # ローディングテキストを削除
        page.controls.remove(loading_text)
        page.update()

    # 天気予報を取得して表示
    def fetch_forecast(e):
        selected_area_name = area_dropdown.value
        if not selected_area_name:
            forecast_output.value = "地域が選択されていません。"
            page.update()
            return

        # 地域名から地域コードを取得（逆引き）
        selected_area_code = None
        for code, name in area_list.items():
            if name == selected_area_name:
                selected_area_code = code
                break

        if not selected_area_code:
            forecast_output.value = "地域コードが見つかりませんでした。"
            page.update()
            return

        forecast_data = fetch_weather_forecast(selected_area_code)
        if forecast_data:
            forecast_output.value = format_weather(forecast_data)
        else:
            forecast_output.value = "天気予報の取得に失敗しました。"
        page.update()

    # UIレイアウト
    page.add(
        ft.Column(
            [
                ft.Text("天気予報アプリ", size=24, weight="bold"),
                ft.Divider(),
                area_dropdown,
                fetch_button,
                ft.Divider(),
                ft.Text("天気予報:", size=18, weight="bold"),
                forecast_output,
            ],
            spacing=10,
            expand=True,
        )
    )

    # ボタンのクリックイベント
    fetch_button.on_click = fetch_forecast

    # アプリ起動時に地域リストをロード
    load_area_list()

# アプリケーションを実行
if __name__ == "__main__":
    ft.app(target=main)


# import requests
# import json
# import flet as ft

# # 地域リストを取得する関数
# def fetch_area_list():
#     """
#     気象庁APIから地域リストを取得する関数
#     """
#     area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
#     try:
#         response = requests.get(area_url)
#         response.raise_for_status()  # HTTPエラーを例外として扱う
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"地域リスト取得エラー: {e}")
#         return None

# # 地域リストを解析して抽出する関数
# def extract_regions(data):
#     """
#     JSONデータから地方の地域リストを抽出する関数。
#     """
#     region_list = {}
#     try:
#         # 最上位のキーに対して処理
#         for key, value in data.items():
#             if isinstance(value, dict) and "name" in value:
#                 # 地方（childrenを持つデータ）のみ抽出
#                 if "children" in value:
#                     region_list[key] = value["name"]
#         return region_list
#     except Exception as e:
#         print(f"地域リスト解析エラー: {e}")
#         return {}

# # 天気予報を取得する関数
# def fetch_weather_forecast(area_code):
#     """
#     指定地域の天気予報を取得する関数
#     """
#     forecast_url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
#     try:
#         response = requests.get(forecast_url)
#         response.raise_for_status()  # HTTPエラーを例外として扱う
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"天気予報取得エラー: {e}")
#         return None

# # Fletアプリケーション
# def main(page: ft.Page):
#     page.title = "天気予報アプリ"
#     page.horizontal_alignment = ft.CrossAxisAlignment.START

#     # UIコンポーネント
#     area_dropdown = ft.Dropdown(width=300, label="地域を選択", options=[])
#     weather_output = ft.Text("")
#     fetch_button = ft.ElevatedButton("天気予報を取得", disabled=True, width=300)
#     area_list = {}

#     # 地域リストを取得し、Dropdownに反映
#     def load_area_list():
#         nonlocal area_list
#         loading_text = ft.Text("地域リストを読み込んでいます...", size=16)
#         page.add(loading_text)
#         page.update()

#         # 地域リストを取得
#         area_data = fetch_area_list()
#         if area_data:
#             # JSONデータを解析
#             area_list = extract_regions(area_data)

#             # デバッグ用：抽出結果を表示
#             print(f"抽出された地域リスト: {json.dumps(area_list, ensure_ascii=False, indent=2)}")

#             # Dropdownに設定
#             area_dropdown.options = [
#                 ft.dropdown.Option(name) for name in area_list.values()
#             ]
#             fetch_button.disabled = False
#         else:
#             print("地域リストを取得できませんでした。")
#             area_dropdown.options = [ft.dropdown.Option("地域データを取得できませんでした")]
#             fetch_button.disabled = True

#         page.controls.remove(loading_text)
#         page.update()

#     # 天気予報を取得して表示
#     def fetch_forecast(e):
#         selected_area_name = area_dropdown.value
#         if not selected_area_name:
#             weather_output.value = "地域が選択されていません。"
#             page.update()
#             return

#         selected_area_code = next(
#             (code for code, name in area_list.items() if name == selected_area_name),
#             None,
#         )

#         if not selected_area_code:
#             weather_output.value = "地域コードが見つかりませんでした。"
#             page.update()
#             return

#         forecast_data = fetch_weather_forecast(selected_area_code)
#         if forecast_data:
#             try:
#                 weather_output.value = json.dumps(forecast_data, ensure_ascii=False, indent=2)
#             except Exception as e:
#                 print(f"天気データ解析エラー: {e}")
#                 weather_output.value = "天気データの解析に失敗しました。"
#         else:
#             weather_output.value = "天気予報の取得に失敗しました。"

#         page.update()

#     # UIレイアウト
#     page.add(
#         ft.Column(
#             [
#                 ft.Text("天気予報アプリ", size=24, weight="bold"),
#                 area_dropdown,
#                 fetch_button,
#                 weather_output,
#             ],
#             spacing=10,
#         )
#     )

#     fetch_button.on_click = fetch_forecast
#     load_area_list()

# # アプリケーションを実行
# if __name__ == "__main__":
#     ft.app(target=main)
