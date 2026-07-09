import os
import threading
import yt_dlp
import flet as ft

def main(page: ft.Page):
    page.title = "YouTube Letöltő"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"

    # --- ÚTVONAL MEGHATÁROZÁSA ---
    if os.path.exists("/storage/emulated/0"):
        download_dir = "/storage/emulated/0/Download"
    elif os.path.exists("D:\\"):
        download_dir = "D:\\XMusic"
    else:
        download_dir = "C:\\XMusic"

    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir, exist_ok=True)
        except Exception:
            pass

    # --- FUNKCIÓK ---
    def clear_link(e):
        url_input.value = ""
        status_text.value = ""
        progress_bar.value = 0
        progress_text.value = "0%"
        page.update()

    def download_thread(url, option, output_dir):
        audio_only = option in [1, 2]
        is_playlist = option in [2, 4]

        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            status_text.value = f"Hiba a mappa ellenőrzésekor: {str(e)}"
            download_btn.disabled = False
            page.update()
            return

        # Sablon beállítása
        file_template = os.path.join(output_dir, "%(title)s.%(ext)s")

        def hook(d):
            if d['status'] == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                percent = downloaded / total
                progress_bar.value = percent
                progress_text.value = f"{int(percent * 100)}%"
                page.update()

        # Úgy állítjuk be, hogy beépített letöltőt használjon, amihez NEM kell FFmpeg
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': file_template,
            'noplaylist': not is_playlist,
            'progress_hooks': [hook],
            'nocheckcertificate': True,
            'rm_cachedir': True,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }

        try:
            status_text.value = "Letöltés folyamatban..."
            page.update()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            status_text.value = f"Sikeres letöltés! Mentve ide:\n{output_dir}"
            progress_bar.value = 1.0
            progress_text.value = "100%"
        except Exception as e:
            status_text.value = f"Hiba: {str(e)}"
        
        download_btn.disabled = False
        page.update()

    def start_download(e):
        if not url_input.value:
            status_text.value = "Kérlek, adj meg egy linket!"
            page.update()
            return
        
        if not path_input.value:
            status_text.value = "Kérlek, adj meg egy mentési útvonalat!"
            page.update()
            return
        
        download_btn.disabled = True
        progress_bar.value = 0
        progress_text.value = "0%"
        status_text.value = "Indítás..."
        page.update()

        threading.Thread(
            target=download_thread, 
            args=(url_input.value, int(options_dropdown.value), path_input.value.strip()), 
            daemon=True
        ).start()

    # --- GUI ELEMEK ---
    url_input = ft.TextField(label="YouTube Link", hint_text="Illeszd be a linket ide...", expand=True)
    clear_btn = ft.IconButton(icon=ft.Icons.CLEAR, on_click=clear_link, tooltip="Mező törlése")
    url_row = ft.Row([url_input, clear_btn], alignment=ft.MainAxisAlignment.CENTER)

    path_input = ft.TextField(label="Mentési mappa (módosítható)", value=download_dir)

    options_dropdown = ft.Dropdown(
        label="Letöltési mód",
        value="1",
        options=[
            ft.dropdown.Option("1", "Egy videó Audióként"),
            ft.dropdown.Option("2", "Lejátszási lista Audióként"),
            ft.dropdown.Option("3", "Egy videó Videóként (MP4)"),
            ft.dropdown.Option("4", "Lejátszási lista Videóként (MP4)"),
        ]
    )

    progress_bar = ft.ProgressBar(value=0, width=400)
    progress_text = ft.Text("0%")
    status_text = ft.Text("", text_align=ft.TextAlign.CENTER)
    
    download_btn = ft.ElevatedButton(
        "Letöltés indítása", 
        on_click=start_download, 
        bgcolor=ft.Colors.GREEN_700, 
        color=ft.Colors.WHITE
    )

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("YouTube Letöltő v2", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Divider(),
                url_row,
                path_input,
                options_dropdown,
                ft.Row([progress_bar, progress_text], alignment=ft.MainAxisAlignment.CENTER),
                status_text,
                ft.Row([download_btn], alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=15),
            padding=10
        )
    )

if __name__ == "__main__":
    ft.run(main)
