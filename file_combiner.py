import tkinter as tk
from tkinter import filedialog, ttk
import os
import datetime
from tkinter import messagebox
import json
import sys
from pathlib import Path

class FileMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("파일 합치기 프로그램")
        self.root.geometry("750x550")
        self.root.configure(bg="#f0f0f0")
        
        # 설정 파일 경로 - 사용자 홈 디렉토리의 특별한 폴더에 저장
        self.app_data_dir = os.path.join(Path.home(), '.file_merger')
        if not os.path.exists(self.app_data_dir):
            os.makedirs(self.app_data_dir)
        self.settings_file = os.path.join(self.app_data_dir, "settings.json")
        
        # 파일 정보를 저장할 리스트
        self.files = []
        self.file_paths = {}  # 파일 경로 저장용 딕셔너리
        self.save_path = None  # 저장 경로를 기억하는 변수 추가
        self.favorites = {}  # 즐겨찾기 그룹 (이름: [파일 경로들])
        self.favorites_window = None  # 즐겨찾기 창 참조
        
        # 저장된 설정 로드
        self.load_settings()
        
        # 메인 프레임 생성
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 제목 라벨
        title_label = tk.Label(
            main_frame, 
            text="✨ 파일 합치기 프로그램 ✨", 
            font=("맑은 고딕", 18, "bold"),
            bg="#f0f0f0",
            fg="#ff6699"
        )
        title_label.pack(pady=10)
        
        # 버튼 프레임
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=10)
        
        # 파일 추가 버튼
        add_button = tk.Button(
            button_frame, 
            text="파일 추가하기 📂", 
            command=self.add_files,
            bg="#ff6699",
            fg="white",
            font=("맑은 고딕", 10),
            relief=tk.RIDGE,
            borderwidth=3,
            padx=10,
            width=15
        )
        add_button.pack(side=tk.LEFT, padx=5)
        
        # 파일 새로고침 버튼
        refresh_button = tk.Button(
            button_frame, 
            text="파일 새로고침 🔄", 
            command=self.refresh_files,
            bg="#66aaff",
            fg="white",
            font=("맑은 고딕", 10),
            relief=tk.RIDGE,
            borderwidth=3,
            padx=10,
            width=15
        )
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 합칠 경로 지정 버튼 추가
        set_path_button = tk.Button(
            button_frame, 
            text="합칠 경로 지정 📌", 
            command=self.set_save_path,
            bg="#ff9966",
            fg="white",
            font=("맑은 고딕", 10),
            relief=tk.RIDGE,
            borderwidth=3,
            padx=10,
            width=15
        )
        set_path_button.pack(side=tk.LEFT, padx=5)
        
        # 전체 삭제 버튼
        delete_all_button = tk.Button(
            button_frame, 
            text="전체 삭제 🚮", 
            command=self.delete_all_files,
            bg="#ff6666",
            fg="white",
            font=("맑은 고딕", 10),
            relief=tk.RIDGE,
            borderwidth=3,
            padx=10,
            width=11
        )
        delete_all_button.pack(side=tk.LEFT, padx=5)
        
        # 파일 합치기 버튼
        merge_button = tk.Button(
            button_frame, 
            text="파일 합치기 💖", 
            command=self.merge_files,
            bg="#66cc99",
            fg="white",
            font=("맑은 고딕", 10, "bold"),
            relief=tk.RIDGE,
            borderwidth=3,
            padx=10,
            width=12
        )
        merge_button.pack(side=tk.LEFT, padx=5)
        
        # 파일 목록 라벨과 즐겨찾기 버튼을 위한 프레임
        file_header_frame = tk.Frame(main_frame, bg="#f0f0f0")
        file_header_frame.pack(fill=tk.X, pady=(20, 5))
        
        # 파일 목록 라벨
        files_label = tk.Label(
            file_header_frame, 
            text="📋 추가된 파일 목록", 
            font=("맑은 고딕", 12, "bold"),
            bg="#f0f0f0"
        )
        files_label.place(x=0, y=0)
        
        # 즐겨찾기 추가 버튼 (절대 위치)
        add_favorite_button = tk.Button(
            file_header_frame,
            text="즐겨찾기 추가 ⭐",
            command=self.add_to_favorites,
            bg="#FFD700",
            fg="#333333",
            font=("맑은 고딕", 9),
            relief=tk.RIDGE,
            borderwidth=2,
            padx=8,
            height=1
        )
        add_favorite_button.place(x=450, y=0)  # 440 + 10 = 450
        
        # 즐겨찾기 목록 버튼 (절대 위치)
        favorites_list_button = tk.Button(
            file_header_frame,
            text="즐겨찾기 목록 📋",
            command=self.show_favorites_list,
            bg="#FFD700",
            fg="#333333",
            font=("맑은 고딕", 9),
            relief=tk.RIDGE,
            borderwidth=2,
            padx=8,
            height=1
        )
        favorites_list_button.place(x=570, y=0)  # 540 + 30 = 570 (버튼 간격 확보)
        
        # 프레임 높이 설정
        file_header_frame.configure(height=30)

        # 두 번째 줄 프레임 생성
        second_row_frame = tk.Frame(main_frame, bg="#f0f0f0")
        second_row_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 체크버튼 변수 추가
        self.topmost_var = tk.BooleanVar(value=False)

        # 항상 맨 위로 버튼 배치
        self.topmost_check = tk.Checkbutton(
            second_row_frame,
            text="항상 맨 위로 📌",
            variable=self.topmost_var,
            command=self.toggle_topmost,
            bg="#f0f0f0",
            fg="#CC66FF",
            selectcolor="white",
            font=("맑은 고딕", 10, "bold"),
            activebackground="#f0f0f0",
            activeforeground="#9933FF",
            padx=5
        )
        self.topmost_check.pack(side=tk.LEFT, padx=5)
        
        # 경로 정보 표시 라벨
        save_path_text = "저장 경로: 아직 지정되지 않았어요"
        if self.save_path:
            save_path_text = f"저장 경로: {self.save_path}"
            
        self.path_label = tk.Label(
            second_row_frame,
            text=f"{save_path_text} 📌", 
            font=("맑은 고딕", 9),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.path_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # 트리뷰와 스크롤바를 감싸는 프레임 만들기!
        tree_frame = tk.Frame(main_frame, bg="#f0f0f0")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 파일 목록 표시할 트리뷰 (다중 선택 가능하도록 설정)
        columns = ('filename', 'path', 'size')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10, selectmode='extended')

        # 스타일 설정
        style = ttk.Style()
        style.configure("Treeview", font=("맑은 고딕", 10))
        style.configure("Treeview.Heading", font=("맑은 고딕", 10, "bold"))

        # 헤더 설정
        self.tree.heading('filename', text='파일명')
        self.tree.heading('path', text='경로')
        self.tree.heading('size', text='크기')

        # 열 너비 설정
        self.tree.column('filename', width=150)
        self.tree.column('path', width=350)
        self.tree.column('size', width=100)

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 스크롤바 위치 지정하기
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 트리뷰에 우클릭 메뉴 추가
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="선택한 파일 삭제 ❌", command=self.remove_selected_files)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 상태 표시 라벨
        self.status_label = tk.Label(
            main_frame, 
            text="파일을 추가해주세요! 💕", 
            font=("맑은 고딕", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.status_label.pack(pady=10)
        
        # 프로그램을 시작할 때 설정이 로드됐음을 표시
        if self.save_path:
            self.status_label.config(text=f"이전 설정을 불러왔어요! 저장 경로가 설정되어 있어요! 📌")
        
        # 드래그 앤 드롭 설정 (tkinterdnd2가 사용 가능한 경우)
        try:
            from tkinterdnd2 import DND_FILES
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.drop)
        except Exception as e:
            # tkinterdnd2를 import 할 수 없는 경우 드래그 앤 드롭 기능 비활성화
            print(f"드래그 앤 드롭 비활성화 오류: {str(e)}")
            self.status_label.config(text="⚠️ 드래그 앤 드롭이 비활성화되었어요!")
    
    def load_settings(self):
        """저장된 설정을 로드합니다."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.save_path = settings.get('save_path', None)
                    
                    # 즐겨찾기 데이터 호환성 처리
                    favorites_data = settings.get('favorites', {})
                    if isinstance(favorites_data, list):
                        # 이전 버전 (리스트) -> 새 버전 (딕셔너리)로 변환
                        self.favorites = {}
                        print("이전 버전 즐겨찾기 데이터 변환 중...")
                    else:
                        self.favorites = favorites_data
                    
                    print(f"설정 로드 성공: {self.save_path}")
                    print(f"즐겨찾기 {len(self.favorites)}개 로드")
            else:
                print("설정 파일이 존재하지 않음")
        except Exception as e:
            print(f"설정 로드 중 오류 발생: {str(e)}")
            # 오류 발생 시 기본값 사용
            self.save_path = None
            self.favorites = {}
    
    def save_settings(self):
        """현재 설정을 저장합니다."""
        try:
            settings = {
                'save_path': self.save_path,
                'favorites': self.favorites
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
                print(f"설정 저장 성공: {self.save_path}")
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {str(e)}")
            messagebox.showwarning("알림", f"설정 저장 중 오류가 발생했어요: {str(e)}")
    
    def add_files(self):
        """파일 탐색기를 열어 파일을 추가합니다."""
        filetypes = (
            ('모든 파일', '*.*'),
            ('Java 파일', '*.java'),
            ('텍스트 파일', '*.txt'),
        )
        
        files = filedialog.askopenfilenames(
            title='파일 선택',
            filetypes=filetypes
        )
        
        if files:
            for file_path in files:
                self.add_file_to_list(file_path)
            
            self.status_label.config(text=f"{len(files)}개의 파일이 추가되었어요! 😊")
    
    def add_file_to_list(self, file_path):
        """목록에 파일을 추가합니다."""
        if file_path in self.file_paths:
            return  # 이미 추가된 파일이면 건너뜀
        
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        size_str = self.format_size(file_size)
        
        # 트리뷰에 추가
        item_id = self.tree.insert('', tk.END, values=(filename, file_path, size_str))
        
        # 파일 경로 저장
        self.file_paths[file_path] = item_id
    
    def format_size(self, size):
        """파일 크기를 읽기 쉬운 형식으로 변환합니다."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def refresh_files(self):
        """파일 목록을 새로고침합니다."""
        # 기존 파일 경로 복사
        old_paths = list(self.file_paths.keys())
        
        if not old_paths:
            self.status_label.config(text="새로고침할 파일이 없어요! 😅")
            return
        
        # 트리뷰 초기화
        self.tree.delete(*self.tree.get_children())
        self.file_paths = {}
        
        # 각 파일의 최신 버전을 다시 추가
        refreshed_count = 0
        for path in old_paths:
            if os.path.exists(path):
                self.add_file_to_list(path)
                refreshed_count += 1
        
        self.status_label.config(text=f"{refreshed_count}개의 파일을 새로고침했어요! 🔄")
    
    def set_save_path(self):
        """저장 경로를 설정합니다."""
        folder_path = filedialog.askdirectory(title='파일을 저장할 폴더 선택')
        
        if folder_path:
            self.save_path = os.path.join(folder_path, "merged_files.txt")
            self.path_label.config(text=f"저장 경로: {self.save_path} 📌")
            self.status_label.config(text=f"저장 경로가 설정되었어요! 📌")
            
            # 설정 저장
            self.save_settings()
    
    def remove_selected_files(self):
        """선택한 여러 파일을 목록에서 제거합니다."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        removed_count = 0
        for item in selected_items:
            # 선택한 항목의 파일 경로 가져오기
            file_path = self.tree.item(item, 'values')[1]
            
            # 트리뷰에서 항목 삭제
            self.tree.delete(item)
            
            # 저장된 파일 경로에서도 삭제
            if file_path in self.file_paths:
                del self.file_paths[file_path]
                removed_count += 1
        
        self.status_label.config(text=f"{removed_count}개의 파일이 삭제되었어요! ❌")
    
    def delete_all_files(self):
        """추가된 모든 파일을 목록에서 제거합니다."""
        if not self.file_paths:
            self.status_label.config(text="삭제할 파일이 없어요! 😅")
            return
            
        # 확인 메시지 표시
        if messagebox.askyesno("확인", "정말로 모든 파일을 목록에서 삭제할까요?"):
            # 트리뷰에서 모든 항목 삭제
            self.tree.delete(*self.tree.get_children())
            
            # 파일 경로 목록 초기화
            file_count = len(self.file_paths)
            self.file_paths = {}
            
            self.status_label.config(text=f"{file_count}개의 파일이 모두 삭제되었어요! 🗑️")
    
    def show_context_menu(self, event):
        """마우스 우클릭 메뉴를 표시합니다."""
        # 클릭한 위치의 항목
        item = self.tree.identify_row(event.y)
        if item:
            # 다중 선택 유지
            # 이미 선택된 항목이 아닌 경우에만 선택 처리
            if item not in self.tree.selection():
                # Ctrl 키를 누르고 있는 것처럼 선택을 추가
                self.tree.selection_add(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def drop(self, event):
        """드래그 앤 드롭으로 파일을 추가합니다."""
        files = self.root.tk.splitlist(event.data)
        count = 0
        for file in files:
            # Windows에서 경로 처리 (작은따옴표 제거)
            file = file.strip("'")
            if os.path.isfile(file):
                self.add_file_to_list(file)
                count += 1
        
        if count > 0:
            self.status_label.config(text=f"{count}개의 파일이 추가되었어요! 🎯")
    
    def merge_files(self):
        """추가된 모든 파일을 하나의 텍스트 파일로 합칩니다."""
        if not self.file_paths:
            messagebox.showwarning("경고", "합칠 파일이 없어요! 먼저 파일을 추가해주세요~ 😅")
            return
        
        # 저장 경로가 지정되어 있지 않으면 사용자에게 물어봄
        save_path = self.save_path
        if not save_path:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("텍스트 파일", "*.txt")],
                title="파일 저장하기"
            )
            
            if not save_path:
                return  # 저장 취소
            
            # 새로 지정한 경로 저장
            self.save_path = save_path
            self.path_label.config(text=f"저장 경로: {self.save_path} 📌")
            self.save_settings()
        
        try:
            with open(save_path, 'w', encoding='utf-8') as output_file:
                # 헤더 정보 작성
                now = datetime.datetime.now()
                output_file.write("================================================================\n")
                output_file.write("파일 합치기 결과\n")
                output_file.write("================================================================\n\n")
                output_file.write(f"이 파일은 {now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}에 생성되었습니다.\n\n")
                output_file.write("용도:\n")
                output_file.write("--------\n")
                output_file.write("이 파일은 여러 파일의 내용을 모아놓은 것입니다.\n")
                output_file.write("쉽게 분석하고 검토할 수 있도록 설계되었습니다.\n\n")
                
                # 파일 형식 정보
                output_file.write("파일 형식:\n")
                output_file.write("------------\n")
                output_file.write("이 내용은 다음과 같이 구성되어 있습니다:\n")
                output_file.write("1. 이 헤더 섹션\n")
                output_file.write("2. 파일 구조\n")
                output_file.write("3. 여러 파일 항목이 있으며 각각 다음으로 구성됩니다:\n")
                output_file.write("  a. 구분선 (================)\n")
                output_file.write("  b. 파일 경로 (File: path/to/file)\n")
                output_file.write("  c. 또 다른 구분선\n")
                output_file.write("  d. 파일의 전체 내용\n")
                output_file.write("  e. 빈 줄\n\n")
                
                # 파일 구조 섹션
                output_file.write("================================================================\n")
                output_file.write("파일 구조\n")
                output_file.write("================================================================\n")
                
                # 모든 파일 경로 목록 작성
                for file_path in self.file_paths.keys():
                    filename = os.path.basename(file_path)
                    output_file.write(f"{file_path}\n")
                
                # 파일 내용 섹션
                output_file.write("\n================================================================\n")
                output_file.write("파일 내용\n")
                output_file.write("================================================================\n\n")
                
                # 각 파일의 내용 추가
                for file_path in self.file_paths.keys():
                    filename = os.path.basename(file_path)
                    
                    output_file.write("================\n")
                    output_file.write(f"File: {file_path}\n")
                    output_file.write("================\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as input_file:
                            content = input_file.read()
                            output_file.write(content)
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, 'r', encoding='cp949') as input_file:
                                content = input_file.read()
                                output_file.write(content)
                        except Exception as e:
                            output_file.write(f"[파일을 읽을 수 없습니다: {str(e)}]\n")
                    except Exception as e:
                        output_file.write(f"[파일을 읽을 수 없습니다: {str(e)}]\n")
                    
                    output_file.write("\n")
            
            # 성공 메시지
            messagebox.showinfo("성공", f"파일이 성공적으로 저장되었어요!\n{save_path} 💖")
            
            # 저장된 파일 폴더 열기
            try:
                folder_path = os.path.dirname(save_path)
                os.startfile(folder_path)
            except:
                # 폴더 열기 실패해도 무시
                pass
                
        except Exception as e:
            messagebox.showerror("오류", f"파일 저장 중 오류가 발생했어요 😢\n{str(e)}")
            
    def toggle_topmost(self):
        """창을 항상 위로 놓거나 해제합니다."""
        if self.topmost_var.get():  # 체크박스가 체크되었을 때!
            self.root.attributes('-topmost', True)
            self.status_label.config(text="창이 항상 맨 위에 고정됐어요! 🔝")
        else:  # 체크 해제되었을 때~
            self.root.attributes('-topmost', False)
            self.status_label.config(text="창 고정이 해제됐어요! 🔄")

    def add_to_favorites(self):
        """현재 파일 목록을 즐겨찾기 그룹으로 저장"""
        if not self.file_paths:
            messagebox.showwarning("경고", "즐겨찾기로 저장할 파일이 없어요! 먼저 파일을 추가해주세요~ 💛")
            return
        
        # 이름 입력 다이얼로그
        dialog = tk.Toplevel(self.root)
        dialog.title("즐겨찾기 이름 지정")
        dialog.geometry("400x150")
        dialog.configure(bg="#f0f0f0")
        
        # 중앙 정렬
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 안내 라벨
        label = tk.Label(
            dialog,
            text="즐겨찾기 이름을 입력해주세요~ 💕",
            font=("맑은 고딕", 11),
            bg="#f0f0f0"
        )
        label.pack(pady=20)
        
        # 입력 필드
        entry = tk.Entry(
            dialog,
            font=("맑은 고딕", 10),
            width=30
        )
        entry.pack(pady=5)
        entry.focus()
        
        # 버튼 프레임
        button_frame = tk.Frame(dialog, bg="#f0f0f0")
        button_frame.pack(pady=15)
        
        def save_favorite():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("경고", "이름을 입력해주세요! 😅")
                return
            
            if name in self.favorites:
                if messagebox.askyesno("확인", f"'{name}' 즐겨찾기가 이미 있어요!\n덮어쓸까요? 🤔"):
                    self.favorites[name] = list(self.file_paths.keys())
                else:
                    return
            else:
                self.favorites[name] = list(self.file_paths.keys())
            
            self.save_settings()
            messagebox.showinfo("성공", f"'{name}' 즐겨찾기로 {len(self.file_paths)}개 파일을 저장했어요! ⭐")
            dialog.destroy()
        
        # 저장 버튼
        save_button = tk.Button(
            button_frame,
            text="저장 ✨",
            command=save_favorite,
            bg="#66cc99",
            fg="white",
            font=("맑은 고딕", 10),
            relief=tk.RIDGE,
            borderwidth=2,
            padx=20
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # 취소 버튼
        cancel_button = tk.Button(
            button_frame,
            text="취소",
            command=dialog.destroy,
            bg="#999999",
            fg="white",
            font=("맑은 고딕", 10),
            relief=tk.RIDGE,
            borderwidth=2,
            padx=20
        )
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Enter 키로 저장
        entry.bind('<Return>', lambda e: save_favorite())
    
    def show_favorites_list(self):
        """즐겨찾기 목록을 보여주는 팝업 창"""
        if not self.favorites:
            messagebox.showinfo("알림", "즐겨찾기가 비어있어요! 파일을 추가해주세요~ 💕")
            return
        
        # 이미 창이 열려있으면 맨 위로 올리고 포커스
        if self.favorites_window and self.favorites_window.winfo_exists():
            self.favorites_window.lift()  # 창을 맨 위로
            self.favorites_window.focus_force()  # 포커스 주기
            # 창 깜빡이기 효과
            self.favorites_window.bell()
            return
        
        # 팝업 창 생성
        self.favorites_window = tk.Toplevel(self.root)
        self.favorites_window.title("즐겨찾기 목록 ⭐")
        self.favorites_window.geometry("800x500")
        self.favorites_window.configure(bg="#f0f0f0")
        
        # 창이 닫힐 때 참조 제거
        def on_close():
            self.favorites_window.destroy()
            self.favorites_window = None
        
        self.favorites_window.protocol("WM_DELETE_WINDOW", on_close)
        
        # 제목
        title_label = tk.Label(
            self.favorites_window,
            text="⭐ 즐겨찾기 그룹 목록 ⭐",
            font=("맑은 고딕", 14, "bold"),
            bg="#f0f0f0",
            fg="#333333"  # 검은색으로 변경
        )
        title_label.pack(pady=10)
        
        # 메인 프레임 (왼쪽: 그룹 리스트, 오른쪽: 파일 리스트)
        main_frame = tk.Frame(self.favorites_window, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 왼쪽 프레임 (즐겨찾기 그룹)
        left_frame = tk.Frame(main_frame, bg="#f0f0f0")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        
        # 그룹 라벨
        group_label = tk.Label(
            left_frame,
            text="📁 즐겨찾기 그룹",
            font=("맑은 고딕", 11, "bold"),
            bg="#f0f0f0"
        )
        group_label.pack(pady=(0, 5))
        
        # 그룹 리스트박스 프레임
        group_list_frame = tk.Frame(left_frame, bg="#f0f0f0")
        group_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 그룹 스크롤바
        group_scrollbar = tk.Scrollbar(group_list_frame)
        group_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 그룹 리스트박스
        group_listbox = tk.Listbox(
            group_list_frame,
            yscrollcommand=group_scrollbar.set,
            font=("맑은 고딕", 10),
            width=25,
            bg="white",
            selectbackground="#FFD700",
            selectforeground="#333333"
        )
        group_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        group_scrollbar.config(command=group_listbox.yview)
        
        # 그룹 버튼들
        group_button_frame = tk.Frame(left_frame, bg="#f0f0f0")
        group_button_frame.pack(fill=tk.X, pady=5)
        
        # 그룹 삭제 버튼
        delete_group_button = tk.Button(
            group_button_frame,
            text="그룹 삭제 🗑️",
            command=lambda: self.delete_favorite_group(group_listbox, self.favorites_window),
            bg="#ff6666",
            fg="white",
            font=("맑은 고딕", 9),
            relief=tk.RIDGE,
            borderwidth=2
        )
        delete_group_button.pack(fill=tk.X, padx=2)
        
        # 오른쪽 프레임 (파일 리스트)
        right_frame = tk.Frame(main_frame, bg="#f0f0f0")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 파일 라벨
        file_label = tk.Label(
            right_frame,
            text="📄 파일 목록",
            font=("맑은 고딕", 11, "bold"),
            bg="#f0f0f0"
        )
        file_label.pack(pady=(0, 5))
        
        # 파일 리스트박스 프레임
        file_list_frame = tk.Frame(right_frame, bg="#f0f0f0")
        file_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 파일 스크롤바
        file_scrollbar = tk.Scrollbar(file_list_frame)
        file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 파일 리스트박스
        file_listbox = tk.Listbox(
            file_list_frame,
            yscrollcommand=file_scrollbar.set,
            font=("맑은 고딕", 10),
            bg="white",
            selectbackground="#66ccff",
            selectforeground="white",
            exportselection=False  # 다른 위젯의 선택 상태에 영향 안 줌
        )
        file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        file_scrollbar.config(command=file_listbox.yview)
        
        # 파일 버튼 프레임
        file_button_frame = tk.Frame(right_frame, bg="#f0f0f0")
        file_button_frame.pack(fill=tk.X, pady=5)
        
        # 파일 추가하기 버튼 (클로저로 current_group_index 캡처)
        def add_files_from_current_group():
            if current_group_index is not None:
                # 임시로 선택 상태 설정
                group_listbox.selection_clear(0, tk.END)
                group_listbox.selection_set(current_group_index)
                self.add_favorites_to_list(group_listbox, self.favorites_window)
            else:
                messagebox.showwarning("경고", "추가할 즐겨찾기 그룹을 선택해주세요! 🎯")
        
        add_files_button = tk.Button(
            file_button_frame,
            text="이 파일들 추가하기 ➕",
            command=add_files_from_current_group,
            bg="#66cc99",
            fg="white",
            font=("맑은 고딕", 10),
            relief=tk.RIDGE,
            borderwidth=2
        )
        add_files_button.pack(fill=tk.X, padx=2)
        
        # 즐겨찾기 그룹 표시
        for favorite_name in self.favorites:
            file_count = len(self.favorites[favorite_name])
            group_listbox.insert(tk.END, f"{favorite_name} ({file_count}개)")
        
        # 현재 선택된 그룹을 추적하는 변수
        current_group_index = None
        
        # 그룹 선택 시 파일 목록 표시
        def on_group_select(event):
            nonlocal current_group_index
            selection = group_listbox.curselection()
            if selection:
                current_group_index = selection[0]
                group_name = list(self.favorites.keys())[current_group_index]
                
                # 파일 리스트 초기화
                file_listbox.delete(0, tk.END)
                
                # 선택된 그룹의 파일들 표시
                for file_path in self.favorites[group_name]:
                    file_listbox.insert(tk.END, file_path)
                
                file_label.config(text=f"📄 {group_name}의 파일 목록 ({len(self.favorites[group_name])}개)")
        
        # 파일 우클릭 메뉴
        file_context_menu = tk.Menu(file_listbox, tearoff=0)
        file_context_menu.add_command(
            label="이 파일 삭제 ❌",
            command=lambda: delete_file_from_favorite()
        )
        
        def delete_file_from_favorite():
            if current_group_index is None:
                return
            
            selection = file_listbox.curselection()
            if not selection:
                messagebox.showwarning("경고", "삭제할 파일을 선택해주세요! 🗑️")
                return
            
            group_name = list(self.favorites.keys())[current_group_index]
            file_index = selection[0]
            file_path = self.favorites[group_name][file_index]
            
            if messagebox.askyesno("확인", f"정말로 이 파일을 즐겨찾기에서 삭제할까요?\n{os.path.basename(file_path)} 🤔"):
                # 파일 삭제
                self.favorites[group_name].pop(file_index)
                
                # 그룹이 비었으면 그룹도 삭제
                if not self.favorites[group_name]:
                    del self.favorites[group_name]
                    messagebox.showinfo("알림", f"'{group_name}' 그룹이 비어서 삭제됐어요! 🗑️")
                    self.favorites_window.destroy()
                    self.show_favorites_list()
                else:
                    # 리스트 업데이트
                    file_listbox.delete(file_index)
                    file_label.config(text=f"📄 {group_name}의 파일 목록 ({len(self.favorites[group_name])}개)")
                    
                    # 그룹 리스트도 업데이트 (파일 개수)
                    group_listbox.delete(current_group_index)
                    group_listbox.insert(current_group_index, f"{group_name} ({len(self.favorites[group_name])}개)")
                    group_listbox.selection_set(current_group_index)
                
                self.save_settings()
                # 성공 메시지 제거 - 바로 반영되니까 따로 알림 필요 없음!
        
        def show_file_context_menu(event):
            try:
                file_listbox.selection_clear(0, tk.END)
                file_listbox.selection_set(file_listbox.nearest(event.y))
                file_context_menu.post(event.x_root, event.y_root)
            except:
                pass
        
        file_listbox.bind("<Button-3>", show_file_context_menu)
        group_listbox.bind('<<ListboxSelect>>', on_group_select)
        
        # 상태 라벨
        status_label = tk.Label(
            self.favorites_window,
            text=f"총 {len(self.favorites)}개의 즐겨찾기 그룹이 있어요! 💖",
            font=("맑은 고딕", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        status_label.pack(pady=5)
    
    def add_favorites_to_list(self, group_listbox, parent_window):
        """선택한 즐겨찾기 그룹의 파일들을 메인 파일 목록에 추가"""
        selection = group_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "추가할 즐겨찾기 그룹을 선택해주세요! 🎯")
            return
        
        index = selection[0]
        group_name = list(self.favorites.keys())[index]
        files_to_add = self.favorites[group_name]
        
        added_count = 0
        for file_path in files_to_add:
            if os.path.exists(file_path):
                if file_path not in self.file_paths.keys():
                    self.add_file_to_list(file_path)
                    added_count += 1
        
        if added_count > 0:
            self.status_label.config(text=f"'{group_name}'에서 {added_count}개의 파일을 추가했어요! 💖")
            parent_window.destroy()
        else:
            messagebox.showinfo("알림", "추가할 수 있는 새로운 파일이 없어요! 😊")
    
    def delete_favorite_group(self, group_listbox, parent_window):
        """선택한 즐겨찾기 그룹 삭제"""
        selection = group_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 그룹을 선택해주세요! 🗑️")
            return
        
        index = selection[0]
        group_name = list(self.favorites.keys())[index]
        
        if messagebox.askyesno("확인", f"'{group_name}' 그룹을 정말 삭제할까요? 🤔"):
            del self.favorites[group_name]
            self.save_settings()
            messagebox.showinfo("성공", f"'{group_name}' 그룹을 삭제했어요! ✨")
            parent_window.destroy()
            self.show_favorites_list()  # 팝업 다시 열기

if __name__ == "__main__":
    # 디버깅용 출력 추가
    print(f"프로그램 시작, 실행 경로: {os.path.abspath(os.path.dirname(sys.argv[0]))}")
    
    try:
        # tkinterdnd2 사용 시도
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
        print("TkinterDnD 로드 성공")
    except ImportError as e:
        # 라이브러리 없으면 일반 Tk 사용
        root = tk.Tk()
        print(f"TkinterDnD 로드 실패: {str(e)}")
        
    app = FileMergerApp(root)
    root.mainloop()