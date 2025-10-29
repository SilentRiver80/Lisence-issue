import customtkinter as ctk
import tkinter as tk  # 변수 및 messagebox 용
from tkinter import messagebox
import smtplib
from email.mime.text import MIMEText
import imaplib
import email
import quopri
import json
import os
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


# ---------------------------
# 설정/토큰 파일 경로
# ---------------------------
CONFIG_PATH = "email_settings.json"
TOKEN_PATH = "last_request.json"

# ---------------------------
# 초기 이메일 설정 (기본값)
# ---------------------------
SMTP_SERVER = 'smtp.naver.com'
SMTP_PORT = 587
IMAP_SERVER = 'imap.naver.com'
EMAIL_ADDRESS = 'ncbrain_smart@naver.com'
EMAIL_PASSWORD = '1J1GHFQ6TVQ4'
RECEIVING_EMAIL_ADDRESS = 'ncbrain.smart@gmail.com'

# ---------------------------
# 초기 디폴트 폼 값
# ---------------------------
DEFAULT_COMPANY_NAME = '엔씨비 정밀'
DEFAULT_LOCK_CODE = ''        # 락번호
DEFAULT_HW_NUMBER = ''        # 하드웨어번호
DEFAULT_PRODUCT_NAME = ''     # 제품명
DEFAULT_MODULE_NAME = ''      # 모듈명
DEFAULT_OPTION_NAME = ''      # 옵션명
DEFAULT_DESCRIPTION = ''      # 설명

# 최근 요청 토큰(메모리)
LAST_TOKEN = None

# ---------------------------
# 공통 유틸
# ---------------------------
def save_settings_to_file():
    data = {
        "SMTP_SERVER": SMTP_SERVER,
        "SMTP_PORT": SMTP_PORT,
        "IMAP_SERVER": IMAP_SERVER,
        "EMAIL_ADDRESS": EMAIL_ADDRESS,
        "EMAIL_PASSWORD": EMAIL_PASSWORD,
        "RECEIVING_EMAIL_ADDRESS": RECEIVING_EMAIL_ADDRESS,
        "DEFAULT_COMPANY_NAME": DEFAULT_COMPANY_NAME,
        "DEFAULT_LOCK_CODE": DEFAULT_LOCK_CODE,
        "DEFAULT_HW_NUMBER": DEFAULT_HW_NUMBER,
        "DEFAULT_PRODUCT_NAME": DEFAULT_PRODUCT_NAME,
        "DEFAULT_MODULE_NAME": DEFAULT_MODULE_NAME,
        "DEFAULT_OPTION_NAME": DEFAULT_OPTION_NAME,
        "DEFAULT_DESCRIPTION": DEFAULT_DESCRIPTION,
    }
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("오류", f"설정 파일 저장 실패: {e}")

def load_settings():
    global SMTP_SERVER, SMTP_PORT, IMAP_SERVER, EMAIL_ADDRESS, EMAIL_PASSWORD
    global RECEIVING_EMAIL_ADDRESS, DEFAULT_COMPANY_NAME, DEFAULT_LOCK_CODE
    global DEFAULT_HW_NUMBER, DEFAULT_PRODUCT_NAME, DEFAULT_MODULE_NAME
    global DEFAULT_OPTION_NAME, DEFAULT_DESCRIPTION

    if not os.path.exists(CONFIG_PATH):
        return
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        SMTP_SERVER = data.get("SMTP_SERVER", SMTP_SERVER)
        SMTP_PORT = int(data.get("SMTP_PORT", SMTP_PORT))
        IMAP_SERVER = data.get("IMAP_SERVER", IMAP_SERVER)
        EMAIL_ADDRESS = data.get("EMAIL_ADDRESS", EMAIL_ADDRESS)
        EMAIL_PASSWORD = data.get("EMAIL_PASSWORD", EMAIL_PASSWORD)
        RECEIVING_EMAIL_ADDRESS = data.get("RECEIVING_EMAIL_ADDRESS", RECEIVING_EMAIL_ADDRESS)

        DEFAULT_COMPANY_NAME = data.get("DEFAULT_COMPANY_NAME", DEFAULT_COMPANY_NAME)
        DEFAULT_LOCK_CODE = data.get("DEFAULT_LOCK_CODE", DEFAULT_LOCK_CODE)
        DEFAULT_HW_NUMBER = data.get("DEFAULT_HW_NUMBER", DEFAULT_HW_NUMBER)
        DEFAULT_PRODUCT_NAME = data.get("DEFAULT_PRODUCT_NAME", DEFAULT_PRODUCT_NAME)
        DEFAULT_MODULE_NAME = data.get("DEFAULT_MODULE_NAME", DEFAULT_MODULE_NAME)
        DEFAULT_OPTION_NAME = data.get("DEFAULT_OPTION_NAME", DEFAULT_OPTION_NAME)
        DEFAULT_DESCRIPTION = data.get("DEFAULT_DESCRIPTION", DEFAULT_DESCRIPTION)

    except Exception as e:
        messagebox.showwarning("경고", f"설정 파일 로드 실패: {e}")

def save_last_token(token: str):
    try:
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            json.dump({"token": token, "time": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_last_token():
    global LAST_TOKEN
    if not os.path.exists(TOKEN_PATH):
        LAST_TOKEN = None
        return
    try:
        with open(TOKEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            LAST_TOKEN = data.get("token")
    except Exception:
        LAST_TOKEN = None


from PIL import Image, ImageDraw, ImageFont

def get_logo_pil(logo_path: str = "NCBRAIN LOGO.png", width: int = 220, height: int = 60) -> Image.Image:
    """
    logo.png가 있으면 그 이미지를 리사이즈해서 사용하고,
    없으면 샘플 로고(PIL로 생성)를 반환합니다.
    """
    # 1) 실제 로고 파일 사용
    if os.path.exists(logo_path):
        try:
            im = Image.open(logo_path).convert("RGBA")
            im = im.resize((width, height), Image.LANCZOS)
            return im
        except Exception:
            pass  # 깨졌거나 문제 있으면 샘플 생성으로 폴백

    # 2) 샘플 로고 생성
    im = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)

    # 둥근 사각 배경
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=14, fill=(30, 144, 255, 255))

    # 폰트 준비 (가능하면 Arial, 안되면 기본)
    try:
        font_big = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    txt = "NCBRAIN"
    sub = "LICENSE"

    # Pillow 10+: textbbox로 사이즈 계산
    def text_size(s: str, font):
        # bbox = (left, top, right, bottom)
        bbox = draw.textbbox((0, 0), s, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    w_txt, h_txt = text_size(txt, font_big)
    w_sub, h_sub = text_size(sub, font_small)

    gap = 2
    total_h = h_txt + gap + h_sub
    y0 = (height - total_h) // 2

    x_txt = (width - w_txt) // 2
    x_sub = (width - w_sub) // 2

    draw.text((x_txt, y0), txt, fill="white", font=font_big)
    draw.text((x_sub, y0 + h_txt + gap), sub, fill="white", font=font_small)

    return im






# ---------------------------
# 이메일 전송/수신
# ---------------------------
def send_email(body_text, subject_with_token):
    try:
        msg = MIMEText(body_text)
        msg['Subject'] = subject_with_token
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECEIVING_EMAIL_ADDRESS
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        messagebox.showinfo("성공", "요청 메일이 전송되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"메일 전송 실패: {e}")

def receive_email():
    """수신함에서 마지막 요청 토큰이 포함된 답장만 반환"""
    load_last_token()
    if not LAST_TOKEN:
        return "최근 보낸 요청 토큰이 없습니다. 먼저 메일을 전송해 주세요."

    try:
        with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
            mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            mail.select('inbox')

            # 발신자 기준 1차 필터
            search_criteria = f'(FROM "{RECEIVING_EMAIL_ADDRESS}")'
            status, messages = mail.search(None, search_criteria)
            email_ids = messages[0].split()

            if not email_ids:
                return "새로운 답장이 없습니다."

            # 최신 메일부터 토큰 포함된 메일 찾기
            for email_id in reversed(email_ids):
                status, data = mail.fetch(email_id, '(RFC822)')
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)

                # 제목에 토큰 확인
                subject_header = email.header.decode_header(msg.get("Subject", ""))[0]
                subject_text = subject_header[0].decode(subject_header[1]) if isinstance(subject_header[0], bytes) else subject_header[0]
                token_found = (LAST_TOKEN in subject_text) if subject_text else False

                # 본문 확인
                if not token_found:
                    body_text_accum = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                charset = part.get_content_charset() or 'utf-8'
                                body_text_accum += part.get_payload(decode=True).decode(charset, errors="ignore")
                    else:
                        charset = msg.get_content_charset() or 'utf-8'
                        body_text_accum = msg.get_payload(decode=True).decode(charset, errors="ignore")

                    token_found = LAST_TOKEN in body_text_accum
                    if token_found:
                        return body_text_accum.strip() if body_text_accum.strip() else "(본문이 비어 있습니다.)"
                else:
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                charset = part.get_content_charset() or 'utf-8'
                                return part.get_payload(decode=True).decode(charset, errors="ignore").strip()
                        return "(본문이 비어 있습니다.)"
                    else:
                        charset = msg.get_content_charset() or 'utf-8'
                        return msg.get_payload(decode=True).decode(charset, errors="ignore").strip()

            return "최근 요청에 대한 답장을 찾지 못했습니다."
    except Exception as e:
        return f"이메일 수신 실패: {e}"

# ---------------------------
# CTk 전용 헬퍼
# ---------------------------
def set_ctk_textbox_readonly(tb: ctk.CTkTextbox, value: str):
    tb.configure(state="normal")
    tb.delete("0.0", "end")
    tb.insert("0.0", value)
    tb.configure(state="disabled")

# ---------------------------
# 설정창 (CTk)
# ---------------------------
def configure_email():
    def on_save():
        global SMTP_SERVER, SMTP_PORT, IMAP_SERVER, EMAIL_ADDRESS, EMAIL_PASSWORD
        global RECEIVING_EMAIL_ADDRESS, DEFAULT_COMPANY_NAME, DEFAULT_LOCK_CODE
        global DEFAULT_HW_NUMBER, DEFAULT_PRODUCT_NAME, DEFAULT_MODULE_NAME
        global DEFAULT_OPTION_NAME, DEFAULT_DESCRIPTION

        try:
            SMTP_SERVER = ent_smtp.get().strip()
            SMTP_PORT = int(ent_smtp_port.get().strip())
            IMAP_SERVER = ent_imap.get().strip()
            EMAIL_ADDRESS = ent_email.get().strip()
            EMAIL_PASSWORD = ent_password.get()
            RECEIVING_EMAIL_ADDRESS = ent_receiver.get().strip()

            DEFAULT_COMPANY_NAME = ent_company.get().strip()
            DEFAULT_LOCK_CODE = ent_lock.get().strip()
            DEFAULT_HW_NUMBER = ent_hw.get().strip()
            DEFAULT_PRODUCT_NAME = ent_product.get().strip()
            DEFAULT_MODULE_NAME = ent_module.get().strip()
            DEFAULT_OPTION_NAME = ent_option.get().strip()
            DEFAULT_DESCRIPTION = txt_desc.get("0.0", "end").strip()

            save_settings_to_file()
            apply_settings_to_main_widgets()
            win.destroy()
            messagebox.showinfo("설정", "저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 실패: {e}")

    win = ctk.CTkToplevel(root)
    win.title("이메일 설정 및 기본값")
    win.geometry("420x600+645+100")
    win.attributes("-topmost", True)

    # 제목
    ctk.CTkLabel(win, text="메일 서버 설정", font=("", 14, "bold")).place(x=20, y=10)

    # 메일 서버
    ctk.CTkLabel(win, text="SMTP 서버:").place(x=20, y=50)
    ent_smtp = ctk.CTkEntry(win, width=260); ent_smtp.insert(0, SMTP_SERVER)
    ent_smtp.place(x=140, y=50)

    ctk.CTkLabel(win, text="SMTP 포트:").place(x=20, y=90)
    ent_smtp_port = ctk.CTkEntry(win, width=260); ent_smtp_port.insert(0, str(SMTP_PORT))
    ent_smtp_port.place(x=140, y=90)

    ctk.CTkLabel(win, text="IMAP 서버:").place(x=20, y=130)
    ent_imap = ctk.CTkEntry(win, width=260); ent_imap.insert(0, IMAP_SERVER)
    ent_imap.place(x=140, y=130)

    ctk.CTkLabel(win, text="발신 이메일 주소:").place(x=20, y=170)
    ent_email = ctk.CTkEntry(win, width=260); ent_email.insert(0, EMAIL_ADDRESS)
    ent_email.place(x=140, y=170)

    ctk.CTkLabel(win, text="발신 이메일 비밀번호:").place(x=20, y=210)
    ent_password = ctk.CTkEntry(win, width=260, show="*"); ent_password.insert(0, EMAIL_PASSWORD)
    ent_password.place(x=140, y=210)

    ctk.CTkLabel(win, text="수신 이메일 주소:").place(x=20, y=250)
    ent_receiver = ctk.CTkEntry(win, width=260); ent_receiver.insert(0, RECEIVING_EMAIL_ADDRESS)
    ent_receiver.place(x=140, y=250)

    # 기본값 섹션
    ctk.CTkLabel(win, text="요청 기본값", font=("", 14, "bold")).place(x=20, y=290)

    ctk.CTkLabel(win, text="업체명:").place(x=20, y=330)
    ent_company = ctk.CTkEntry(win, width=260); ent_company.insert(0, DEFAULT_COMPANY_NAME)
    ent_company.place(x=140, y=330)

    ctk.CTkLabel(win, text="락번호:").place(x=20, y=370)
    ent_lock = ctk.CTkEntry(win, width=260); ent_lock.insert(0, DEFAULT_LOCK_CODE)
    ent_lock.place(x=140, y=370)

    ctk.CTkLabel(win, text="하드웨어번호:").place(x=20, y=410)
    ent_hw = ctk.CTkEntry(win, width=260); ent_hw.insert(0, DEFAULT_HW_NUMBER)
    ent_hw.place(x=140, y=410)

    ctk.CTkLabel(win, text="제품명/모듈명/옵션명:").place(x=20, y=450)
    ent_product = ctk.CTkEntry(win, width=80); ent_product.insert(0, DEFAULT_PRODUCT_NAME)
    ent_product.place(x=140, y=450)

    ent_module = ctk.CTkEntry(win, width=80); ent_module.insert(0, DEFAULT_MODULE_NAME)
    ent_module.place(x=225, y=450)

    ent_option = ctk.CTkEntry(win, width=80); ent_option.insert(0, DEFAULT_OPTION_NAME)
    ent_option.place(x=310, y=450)

    ctk.CTkLabel(win, text="설명:").place(x=20, y=490)
    txt_desc = ctk.CTkTextbox(win, width=260, height=60)
    txt_desc.insert("0.0", DEFAULT_DESCRIPTION)
    txt_desc.place(x=140, y=490)

    ctk.CTkButton(win, text="저장", command=on_save, width=120).place(x=280, y=600-40)

# ---------------------------
# 버튼 동작 (root)
# ---------------------------
def request_code():
    company = ent_company_name.get().strip()
    lock_code = ent_lock_code.get().strip()
    hw_num = ent_hw_number.get().strip()
    product = var_product.get().strip()
    module = var_module.get().strip()
    option = var_option.get().strip()
    desc = txt_description.get("0.0", "end").strip()

    if not company:
        messagebox.showerror("오류", "업체명을 입력하세요.")
        return
    if len(lock_code) > 20:
        messagebox.showerror("오류", "락번호는 20자 이내여야 합니다.")
        return

    # 고유 토큰 생성 및 저장
    token = f"REQ:{uuid.uuid4().hex[:8].upper()}"
    global LAST_TOKEN
    LAST_TOKEN = token
    save_last_token(token)

    subject_with_token = f"{company} [{token}]"
    body = (
        f"[라이선스/코드 요청]\n"
        f"- 업체명: {company}\n"
        f"- 락번호: {lock_code}\n"
        f"- 하드웨어번호: {hw_num}\n"
        f"- 제품명: {product}\n"
        f"- 모듈명: {module}\n"
        f"- 옵션명: {option}\n"
        f"- 설명: {desc}\n\n"
        f"(추적 토큰: {token})\n"
    )
    send_email(body, subject_with_token)

def check_response():
    response = receive_email()
    txt_response.configure(state="normal")
    txt_response.delete("0.0", "end")
    txt_response.insert("0.0", response)
    txt_response.configure(state="disabled")

# ---------------------------
# 메인 위젯에 설정값 반영
# ---------------------------
def apply_settings_to_main_widgets():
    try:
        ent_company_name.delete(0, "end")
        ent_company_name.insert(0, DEFAULT_COMPANY_NAME)

        ent_lock_code.delete(0, "end"); ent_lock_code.insert(0, DEFAULT_LOCK_CODE)
        ent_hw_number.delete(0, "end"); ent_hw_number.insert(0, DEFAULT_HW_NUMBER)

        var_product.set(DEFAULT_PRODUCT_NAME)
        var_module.set(DEFAULT_MODULE_NAME)
        var_option.set(DEFAULT_OPTION_NAME)

        set_ctk_textbox_readonly(txt_description, DEFAULT_DESCRIPTION)
    except Exception:
        pass

# ---------------------------
# 앱 시작 (설정 로드)
# ---------------------------
load_settings()
load_last_token()

# ---------------------------
# CTk 테마/루트 구성
# ---------------------------
ctk.set_appearance_mode("System")  # "Light" / "Dark" / "System"
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("NCBrain 라이선스 코드 요청 클라이언트 V0.5")
root.geometry("540x900+100+100")
root.resizable(False, False)

# 상단 설정 버튼
ctk.CTkButton(root, text="설정", command=configure_email, width=80).place(x=440, y=10)

# 업체명 (수정 가능)
ctk.CTkLabel(root, text="업체명 :").place(x=20, y=50)
ent_company_name = ctk.CTkEntry(root, width=360)
ent_company_name.insert(0, DEFAULT_COMPANY_NAME)
ent_company_name.place(x=140, y=50)

# 락번호 / 하드웨어번호 (수정 가능)
ctk.CTkLabel(root, text="락번호 :").place(x=20, y=90)
ent_lock_code = ctk.CTkEntry(root, width=360)
ent_lock_code.insert(0, DEFAULT_LOCK_CODE)
ent_lock_code.place(x=140, y=90)

ctk.CTkLabel(root, text="하드웨어번호 :").place(x=20, y=130)
ent_hw_number = ctk.CTkEntry(root, width=360)
ent_hw_number.insert(0, DEFAULT_HW_NUMBER)
ent_hw_number.place(x=140, y=130)

# 제품/모듈/옵션 (읽기전용 – 설정창에서만 변경)
var_product = tk.StringVar(value=DEFAULT_PRODUCT_NAME)
var_module = tk.StringVar(value=DEFAULT_MODULE_NAME)
var_option = tk.StringVar(value=DEFAULT_OPTION_NAME)

ctk.CTkLabel(root, text="제품명 :").place(x=20, y=170)
ent_product_readonly = ctk.CTkEntry(root, width=360, textvariable=var_product, state="readonly")
ent_product_readonly.place(x=140, y=170)

ctk.CTkLabel(root, text="모듈명 :").place(x=20, y=210)
ent_module_readonly = ctk.CTkEntry(root, width=360, textvariable=var_module, state="readonly")
ent_module_readonly.place(x=140, y=210)

ctk.CTkLabel(root, text="옵션명 :").place(x=20, y=250)
ent_option_readonly = ctk.CTkEntry(root, width=360, textvariable=var_option, state="readonly")
ent_option_readonly.place(x=140, y=250)

# 설명(읽기전용 텍스트박스)
ctk.CTkLabel(root, text="설명/요청 :").place(x=20, y=290)
txt_description = ctk.CTkTextbox(root, width=360, height=110)
txt_description.place(x=140, y=290)
set_ctk_textbox_readonly(txt_description, DEFAULT_DESCRIPTION)

# 요청/응답 버튼
ctk.CTkButton(root, text="요청", width=200, command=request_code).place(x=300, y=410)
ctk.CTkButton(root, text="응답 확인", width=120, command=check_response).place(x=60, y=450)

# 응답 표시 (읽기전용)
ctk.CTkLabel(root, text="응답:").place(x=20, y=450)
txt_response = ctk.CTkTextbox(root, width=480, height=330)
txt_response.place(x=20, y=490)
txt_response.configure(state="disabled")

# 설정값 반영
apply_settings_to_main_widgets()

# ----- 로고 이미지 하단 중앙 배치 -----
# 원하는 크기로 조절
_logo_w, _logo_h = 200, 50
logo_pil = get_logo_pil("NCBRAIN LOGO.png", width=_logo_w, height=_logo_h)

# CTkImage로 변환 (가비지 컬렉션 방지 위해 root에 참조 보관)
root.logo_ctk = ctk.CTkImage(light_image=logo_pil, dark_image=logo_pil, size=(_logo_w, _logo_h))
logo_label = ctk.CTkLabel(root, image=root.logo_ctk, text="")
# 창 최하단 중앙(살짝 위) 위치: relx=0.5(가운데), rely=0.99(거의 바닥), anchor='s'(아래 정렬)
logo_label.place(relx=0.5, rely=0.98, anchor="s")



root.mainloop()


# pyinstaller --onefile --noconsole --icon=ncb.ico lisence_invite_issue.py

