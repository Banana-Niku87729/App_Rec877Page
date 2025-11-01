import os
import shutil
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext
import getpass

class MinecraftSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UWPBEMinecraftToGDKBEMinecraft")
        self.root.geometry("700x500")
        
        # アイコン設定(icon.pngがある場合)
        try:
            icon_path = Path(__file__).parent / "icon.png"
            if icon_path.exists():
                self.root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
        except:
            pass
        
        # ユーザー名取得
        self.username = getpass.getuser()
        
        # パス設定
        self.uwp_path = Path(f"C:/Users/{self.username}/AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang")
        self.gdk_shared_path = Path(f"C:/Users/{self.username}/AppData/Roaming/Minecraft Bedrock/Users/Shared/games/com.mojang")
        
        # UI作成
        self.create_widgets()
        
    def create_widgets(self):
        # タイトル
        title_label = tk.Label(self.root, text="Minecraft Bedrock データ同期ツール", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 説明
        desc_label = tk.Label(self.root, 
                             text="UWP版MinecraftからGDK版Minecraftにデータをコピーします",
                             font=("Arial", 10))
        desc_label.pack(pady=5)
        
        # 実行ボタン
        self.sync_button = tk.Button(self.root, text="同期開始", 
                                     command=self.start_sync,
                                     font=("Arial", 12, "bold"),
                                     bg="#4CAF50", fg="white",
                                     padx=20, pady=10)
        self.sync_button.pack(pady=20)
        
        # ログエリア
        log_label = tk.Label(self.root, text="ログ:", font=("Arial", 10, "bold"))
        log_label.pack(anchor="w", padx=20)
        
        self.log_text = scrolledtext.ScrolledText(self.root, height=15, width=80)
        self.log_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """ログメッセージを表示"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def check_folders_exist(self, base_path, folders):
        """指定されたフォルダが存在するか確認"""
        existing = []
        missing = []
        for folder in folders:
            folder_path = base_path / folder
            if folder_path.exists():
                existing.append(folder)
            else:
                missing.append(folder)
        return existing, missing
    
    def copy_folder_contents(self, src, dst):
        """フォルダの中身をコピー"""
        if not src.exists():
            return False
        
        if not dst.exists():
            dst.mkdir(parents=True)
        
        # フォルダ内のすべてのファイルとフォルダをコピー
        for item in src.iterdir():
            dst_item = dst / item.name
            if item.is_dir():
                if dst_item.exists():
                    shutil.rmtree(dst_item)
                shutil.copytree(item, dst_item)
            else:
                shutil.copy2(item, dst_item)
        return True
    
    def find_uuid_folder(self):
        """UUIDフォルダを検索"""
        users_path = Path(f"C:/Users/{self.username}/AppData/Roaming/Minecraft Bedrock/Users")
        if not users_path.exists():
            return None
        
        for folder in users_path.iterdir():
            if folder.is_dir() and folder.name.isdigit() and folder.name != "Shared":
                return folder
        return None
    
    def start_sync(self):
        """同期処理を開始"""
        self.log_text.delete(1.0, tk.END)
        self.log("=== 同期処理を開始します ===\n")
        
        try:
            # 1. UWPパスの確認
            self.log(f"1. UWP版パスを確認中: {self.uwp_path}")
            if not self.uwp_path.exists():
                self.log("❌ エラー: UWP版Minecraftのフォルダが見つかりません")
                messagebox.showerror("エラー", "UWP版Minecraftのフォルダが見つかりません")
                return
            
            # 必要なフォルダの確認
            required_folders = [
                "behavior_packs", "resource_packs", "custom_skins", "skin_packs",
                "development_behavior_packs", "development_resource_packs",
                "development_skin_packs", "minecraftpe"
            ]
            
            existing, missing = self.check_folders_exist(self.uwp_path, required_folders)
            self.log(f"✓ 存在するフォルダ: {', '.join(existing)}")
            if missing:
                self.log(f"⚠ 存在しないフォルダ: {', '.join(missing)}")
            self.log("")
            
            # 2. GDK Sharedパスの処理
            self.log(f"2. GDK版 Sharedパスを処理中: {self.gdk_shared_path}")
            if not self.gdk_shared_path.exists():
                self.log(f"   フォルダを作成します: {self.gdk_shared_path}")
                self.gdk_shared_path.mkdir(parents=True)
            
            shared_folders = [
                "behavior_packs", "resource_packs",
                "development_behavior_packs", "development_resource_packs",
                "development_skin_packs"
            ]
            
            # Sharedフォルダにコピー
            for folder_name in shared_folders:
                src = self.uwp_path / folder_name
                dst = self.gdk_shared_path / folder_name
                
                if src.exists():
                    self.log(f"   {folder_name} をコピー中...")
                    if self.copy_folder_contents(src, dst):
                        self.log(f"   ✓ {folder_name} のコピー完了")
                    else:
                        self.log(f"   ⚠ {folder_name} のコピーに失敗")
                else:
                    # フォルダが存在しない場合は空フォルダを作成
                    if not dst.exists():
                        dst.mkdir(parents=True)
                        self.log(f"   ✓ {folder_name} を作成(空)")
            self.log("")
            
            # 3. GDK UUIDパスの処理
            self.log("3. GDK版 UUIDフォルダを検索中...")
            uuid_folder = self.find_uuid_folder()
            
            if uuid_folder:
                self.log(f"   ✓ UUIDフォルダを発見: {uuid_folder.name}")
                gdk_uuid_path = uuid_folder / "games" / "com.mojang"
                
                if not gdk_uuid_path.exists():
                    gdk_uuid_path.mkdir(parents=True)
                    self.log(f"   フォルダを作成: {gdk_uuid_path}")
                
                uuid_folders = ["custom_skins", "skin_packs", "minecraftpe"]
                
                for folder_name in uuid_folders:
                    src = self.uwp_path / folder_name
                    dst = gdk_uuid_path / folder_name
                    
                    if folder_name == "minecraftpe":
                        # minecraftpeの場合はexternal_servers.txtのみコピー
                        src_file = src / "external_servers.txt"
                        if src_file.exists():
                            if not dst.exists():
                                dst.mkdir(parents=True)
                            dst_file = dst / "external_servers.txt"
                            shutil.copy2(src_file, dst_file)
                            self.log(f"   ✓ external_servers.txt をコピー")
                        else:
                            if not dst.exists():
                                dst.mkdir(parents=True)
                            self.log(f"   ⚠ external_servers.txt が見つかりません(空フォルダ作成)")
                    else:
                        # その他のフォルダは全てコピー
                        if src.exists():
                            self.log(f"   {folder_name} をコピー中...")
                            if self.copy_folder_contents(src, dst):
                                self.log(f"   ✓ {folder_name} のコピー完了")
                            else:
                                self.log(f"   ⚠ {folder_name} のコピーに失敗")
                        else:
                            if not dst.exists():
                                dst.mkdir(parents=True)
                                self.log(f"   ✓ {folder_name} を作成(空)")
            else:
                self.log("   ⚠ UUIDフォルダが見つかりません")
                self.log("   GDK版Minecraftを一度起動してください")
            
            self.log("\n=== 同期処理が完了しました ===")
            messagebox.showinfo("完了", "データの同期が完了しました!")
            
        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}"
            self.log(f"\n❌ {error_msg}")
            messagebox.showerror("エラー", error_msg)

def main():
    root = tk.Tk()
    app = MinecraftSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()