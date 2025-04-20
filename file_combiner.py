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
        self.root.geometry("700x500")
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
            padx=10
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
            padx=10
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
            padx=10
        )
        set_path_button.pack(side=tk.LEFT, padx=5)
        
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
            padx=10
        )
        merge_button.pack(side=tk.LEFT, padx=5)
        
        # 전체 삭제 버튼
        clear_all_button = tk.Button(
            button_frame, 
            text="전체 삭제 🗑️", 
            command=self.clear_all_files,
            bg="#ff5555",
            fg="white",
            font=("맑은 고딕", 10),
            relief=tk.RIDGE,
            borderwidth=3,
            padx=10
        )
        clear_all_button.pack(side=tk.LEFT, padx=5)
        
        # 파일 목록 라벨
        files_label = tk.Label(
            main_frame, 
            text="📋 추가된 파일 목록", 
            font=("맑은 고딕", 12, "bold"),
            bg="#f0f0f0"
        )
        files_label.pack(pady=(20, 5), anchor=tk.W)
        
        # 경로 정보 표시 라벨
        save_path_text = "저장 경로: 아직 지정되지 않았어요"
        if self.save_path:
            save_path_text = f"저장 경로: {self.save_path}"
            
        self.path_label = tk.Label(
            main_frame,
            text=f"{save_path_text} 📌", 
            font=("맑은 고딕", 9),
            bg="#f0f0f0",
            fg="#666666"
        )
        self.path_label.pack(anchor=tk.W)
        
        # 파일 목록 표시할 트리뷰 (다중 선택 가능하도록 설정)
        columns = ('filename', 'path', 'size')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10, selectmode='extended')
        
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
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
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
                    print(f"설정 로드 성공: {self.save_path}")
            else:
                print("설정 파일이 존재하지 않음")
        except Exception as e:
            print(f"설정 로드 중 오류 발생: {str(e)}")
            # 오류 발생 시 기본값 사용
            self.save_path = None
    
    def save_settings(self):
        """현재 설정을 저장합니다."""
        try:
            settings = {
                'save_path': self.save_path
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
            
    def clear_all_files(self):
        """모든 파일을 목록에서 제거합니다."""
        if not self.file_paths:
            self.status_label.config(text="삭제할 파일이 없어요! 😅")
            return
            
        # 확인 메시지
        confirm = messagebox.askyesno("확인", "모든 파일을 목록에서 제거할까요?")
        if not confirm:
            return
            
        # 트리뷰 초기화
        self.tree.delete(*self.tree.get_children())
        
        # 파일 경로 딕셔너리 초기화
        file_count = len(self.file_paths)
        self.file_paths = {}
        
        self.status_label.config(text=f"{file_count}개의 파일이 모두 삭제되었어요! 🗑️")
    
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