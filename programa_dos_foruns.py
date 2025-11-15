
import time
import re
import os
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pyautogui
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, filedialog
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import json


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


GEMINI_API_KEY = "AIzaSyAPv4TvUFgSATKmR6cVjCwgD41AmD8bKM8"  
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

class RegionSelector:
    
    def __init__(self, callback):
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        
        self.root = tk.Toplevel()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-topmost', True)
        
        self.canvas = tk.Canvas(self.root, cursor="cross", bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        label = tk.Label(self.root, 
                        text=" ARRASTE para selecionar | ESC para cancelar",
                        bg='yellow', fg='black', font=('Arial', 14, 'bold'),
                        padx=20, pady=10)
        label.place(relx=0.5, rely=0.05, anchor='center')
        
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.root.bind('<Escape>', lambda e: self.cancel())
        
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
    
    def on_drag(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=3, fill='yellow', stipple='gray50'
        )
    
    def on_release(self, event):
        if self.start_x and self.start_y:
            x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
            x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
            self.root.destroy()
            if x2 - x1 > 50 and y2 - y1 > 50:
                self.callback((x1, y1, x2-x1, y2-y1))
            else:
                messagebox.showwarning("Aviso", "Área muito pequena!")
    
    def cancel(self):
        self.root.destroy()

def preprocess_image(pil_image):
    
    try:
        img = pil_image.convert('L')
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.2)
        img = img.filter(ImageFilter.SHARPEN)
        
        width, height = img.size
        if width < 800:
            scale = 1200 / width
            img = img.resize((int(width * scale), int(height * scale)), Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        return pil_image

def capture_screenshot(region=None):
    """Captura screenshot."""
    try:
        if region:
            x, y, w, h = region
            return pyautogui.screenshot(region=(x, y, w, h))
        return pyautogui.screenshot()
    except Exception as e:
        print(f"Erro: {e}")
        return None

def ocr_image(pil_image, lang='por+eng'):
    
    try:
        processed = preprocess_image(pil_image)
        text = pytesseract.image_to_string(processed, lang=lang, config='--psm 6 --oem 3')
        return text
    except Exception as e:
        return f"Erro no OCR: {e}"

def ask_gemini_ai(question_text, api_key):
    
    if not api_key or api_key == "SUA_API_KEY_AQUI":
        return {
            'resposta': "❌ Configure sua API Key do Google Gemini primeiro!",
            'explicacao': "Vá em: https://makersuite.google.com/app/apikey e pegue sua chave GRATUITA",
            'alternativa': None
        }
    
    try:
        
        prompt = f"""Você é um assistente educacional. Analise a pergunta abaixo e forneça:

1. A LETRA da alternativa correta (apenas A, B, C, D ou E)
2. Uma explicação breve do porquê está correta
3. Se não conseguir identificar alternativas, apenas responda a pergunta

TEXTO DA PERGUNTA:
{question_text}

RESPONDA NO FORMATO:
RESPOSTA: [letra]
EXPLICAÇÃO: [sua explicação]"""

        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 500
            }
        }
        
        url = f"{GEMINI_API_URL}?key={api_key}"
        
        if HAS_REQUESTS:
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['candidates'][0]['content']['parts'][0]['text']
            else:
                error_msg = response.json().get('error', {}).get('message', 'Erro desconhecido')
                return {
                    'resposta': f"❌ Erro na API: {error_msg}",
                    'explicacao': "Verifique sua API Key ou conexão",
                    'alternativa': None
                }
        else:
            
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
            
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
                ai_text = result['candidates'][0]['content']['parts'][0]['text']
        
        
        resposta_match = re.search(r'RESPOSTA:\s*([A-E])', ai_text, re.IGNORECASE)
        explicacao_match = re.search(r'EXPLICAÇÃO:\s*(.+)', ai_text, re.IGNORECASE | re.DOTALL)
        
        alternativa = resposta_match.group(1).upper() if resposta_match else None
        explicacao = explicacao_match.group(1).strip() if explicacao_match else ai_text
        
        return {
            'resposta': ai_text,
            'explicacao': explicacao,
            'alternativa': alternativa
        }
            
    except Exception as e:
        
        error_message = str(e)
        if 'timeout' in error_message.lower():
            return {
                'resposta': " Timeout - A IA demorou muito para responder",
                'explicacao': "Tente novamente",
                'alternativa': None
            }
        else:
            return {
                'resposta': f"❌ Erro: {error_message}",
                'explicacao': "Verifique sua conexão com internet e API Key",
                'alternativa': None
            }

class StudyApp:
    def __init__(self, root):
        self.root = root
        root.title(" Assistente com IA - Google Gemini")
        root.geometry("1100x800")
        
        self.frame = tk.Frame(root, padx=10, pady=10)
        self.frame.pack(fill='both', expand=True)
        
        
        config_frame = tk.Frame(self.frame, bg='#E1F5FE', padx=10, pady=10)
        config_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        tk.Label(config_frame, text=" API Key do Google Gemini:", 
                bg='#E1F5FE', font=('Arial', 9, 'bold')).pack(side='left')
        
        self.api_key_var = tk.StringVar(value=GEMINI_API_KEY)
        self.api_entry = tk.Entry(config_frame, textvariable=self.api_key_var, 
                                  width=50, font=('Consolas', 9))
        self.api_entry.pack(side='left', padx=5)
        
        btn_help = tk.Button(config_frame, text="❓ Como obter", 
                            command=self.show_api_help, font=('Arial', 8))
        btn_help.pack(side='left', padx=5)
        
        
        if not HAS_REQUESTS:
            tk.Label(config_frame, text=" Biblioteca 'requests' não encontrada (usando urllib)", 
                    bg='#FFF3E0', fg='#E65100', font=('Arial', 8)).pack(side='left', padx=10)
        
        
        btn_frame = tk.Frame(self.frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        btn_select = tk.Button(btn_frame, text=" SELECIONAR ÁREA", 
                              command=self.on_select_region, bg='#FF5722', fg='white',
                              font=('Arial', 11, 'bold'), padx=20, pady=10)
        btn_select.pack(side='left', padx=5)
        
        btn_capture = tk.Button(btn_frame, text=" Tela Inteira", 
                                command=self.on_capture, bg='#4CAF50', fg='white',
                                font=('Arial', 10), padx=15, pady=8)
        btn_capture.pack(side='left', padx=5)
        
        btn_ask_ai = tk.Button(btn_frame, text=" PERGUNTAR À IA", 
                              command=self.ask_ai_manual, bg='#9C27B0', fg='white',
                              font=('Arial', 10, 'bold'), padx=15, pady=8)
        btn_ask_ai.pack(side='left', padx=5)
        
        btn_load = tk.Button(btn_frame, text=" Abrir", 
                            command=self.load_image, bg='#607D8B', 
                            fg='white', font=('Arial', 10), padx=15, pady=8)
        btn_load.pack(side='left', padx=5)
        
        btn_clear = tk.Button(btn_frame, text="", 
                             command=self.clear_all, bg='#FF9800', 
                             fg='white', font=('Arial', 10), padx=12, pady=8)
        btn_clear.pack(side='left', padx=5)
        
        
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=5)
        
       
        tab_ai = tk.Frame(self.notebook)
        self.notebook.add(tab_ai, text=" Resposta da IA")
        
        tk.Label(tab_ai, text=" RESPOSTA GERADA PELA INTELIGÊNCIA ARTIFICIAL", 
                font=('Arial', 12, 'bold'), bg='#E8EAF6', pady=10, fg='#311B92').pack(fill='x')
        
        self.txt_ai = scrolledtext.ScrolledText(tab_ai, width=120, height=28, 
                                                wrap=tk.WORD, font=('Arial', 11),
                                                bg='#FAFAFA')
        self.txt_ai.pack(fill='both', expand=True, padx=8, pady=8)
        
        
        tab_ocr = tk.Frame(self.notebook)
        self.notebook.add(tab_ocr, text=" Texto Capturado")
        
        self.txt_ocr = scrolledtext.ScrolledText(tab_ocr, width=120, height=28, 
                                                 wrap=tk.WORD, font=('Consolas', 9))
        self.txt_ocr.pack(fill='both', expand=True, padx=5, pady=5)
        
        
        action_frame = tk.Frame(self.frame)
        action_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        btn_copy = tk.Button(action_frame, text=" Copiar Resposta", 
                            command=self.copy_ai_response, font=('Arial', 9))
        btn_copy.pack(side='left', padx=5)
        
        btn_save = tk.Button(action_frame, text=" Salvar Imagem", 
                            command=self.save_screenshot, font=('Arial', 9))
        btn_save.pack(side='left', padx=5)
        
        tk.Label(action_frame, text=" Capture a pergunta e clique 'PERGUNTAR À IA'", 
                fg='#9C27B0', font=('Arial', 9, 'bold')).pack(side='left', padx=20)
        
        btn_quit = tk.Button(action_frame, text="❌ Sair", 
                            command=root.quit, font=('Arial', 9))
        btn_quit.pack(side='right', padx=5)
        
        
        self.status = tk.Label(self.frame, text="✓ Configure sua API Key e capture uma pergunta", 
                              anchor='w', relief=tk.SUNKEN, bg='#E0E0E0', padx=5,
                              font=('Arial', 9))
        self.status.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(10,0))
        
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        self.last_text = ""
        self.last_screenshot = None
        self.last_ai_response = None

    def show_api_help(self):
        
        msg = """ COMO OBTER SUA API KEY GRATUITA:

1. Acesse: https://makersuite.google.com/app/apikey"""
        
        messagebox.showinfo("Como obter API Key", msg)

    def set_status(self, txt):
        self.status.config(text=txt)
        self.root.update_idletasks()

    def on_select_region(self):
        self.set_status(" Selecione a área...")
        self.root.update()
        time.sleep(0.3)
        RegionSelector(self.capture_region)

    def capture_region(self, region):
        self.set_status(f" Capturando {region[2]}x{region[3]}px...")
        self.root.update()
        time.sleep(0.2)
        im = capture_screenshot(region)
        self.process_image(im, auto_ask=True)

    def on_capture(self):
        self.set_status(" Capturando tela...")
        self.root.update()
        time.sleep(0.3)
        im = capture_screenshot()
        self.process_image(im, auto_ask=True)

    def load_image(self):
        filename = filedialog.askopenfilename(
            title="Selecione imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp"), ("Todos", "*.*")]
        )
        if filename:
            try:
                im = Image.open(filename)
                self.set_status(f" {os.path.basename(filename)}")
                self.process_image(im, auto_ask=False)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}")

    def process_image(self, im, auto_ask=False):
        if not im:
            return
        
        self.last_screenshot = im
        self.set_status(" Processando OCR...")
        self.root.update()
        
        text = ocr_image(im)
        self.last_text = text
        
        self.txt_ocr.delete('1.0', tk.END)
        self.txt_ocr.insert(tk.END, text)
        
        if text.strip() and len(text.strip()) > 20:
            self.set_status(f"✓ {len(text)} caracteres extraídos")
            if auto_ask:
                self.ask_ai_manual()
        else:
            self.set_status(" Pouco texto detectado")
            messagebox.showwarning("Aviso", "Pouco texto! Use 'Selecionar Área' na pergunta.")

    def ask_ai_manual(self):
       
        if not self.last_text or len(self.last_text.strip()) < 10:
            messagebox.showwarning("Aviso", "Capture uma pergunta primeiro!")
            return
        
        api_key = self.api_key_var.get().strip()
        if not api_key or api_key == "SUA_API_KEY_AQUI" or api_key == "AIzaSyDSBms7w7RwhX7Pt-2R0-2bMTdATPzqh1o":
            messagebox.showwarning("API Key", 
                "Configure sua API Key do Google Gemini!\n\n"
                "A chave no código é apenas um exemplo.\n"
                "Clique em ' Como obter' para instruções.")
            return
        
        self.set_status(" Consultando IA... Aguarde...")
        self.txt_ai.delete('1.0', tk.END)
        self.txt_ai.insert(tk.END, "⏳ Aguardando resposta da IA...\n\n")
        self.txt_ai.insert(tk.END, "Isso pode levar alguns segundos...\n")
        self.root.update()
        
        try:
            
            resultado = ask_gemini_ai(self.last_text, api_key)
            self.last_ai_response = resultado
            
            
            self.txt_ai.delete('1.0', tk.END)
            
            if resultado['alternativa']:
                
                self.txt_ai.insert(tk.END, " RESPOSTA CORRETA\n", 'header')
                self.txt_ai.insert(tk.END, "="*100 + "\n\n", 'divider')
                
                self.txt_ai.insert(tk.END, f" ALTERNATIVA: ", 'label')
                self.txt_ai.insert(tk.END, f"{resultado['alternativa']}\n\n", 'answer')
                
                self.txt_ai.insert(tk.END, " EXPLICAÇÃO:\n", 'label')
                self.txt_ai.insert(tk.END, f"{resultado['explicacao']}\n\n", 'explanation')
                
                self.txt_ai.insert(tk.END, "="*100 + "\n\n", 'divider')
                self.txt_ai.insert(tk.END, " RESPOSTA COMPLETA DA IA:\n", 'label')
                self.txt_ai.insert(tk.END, resultado['resposta'], 'full')
                
            else:
                
                self.txt_ai.insert(tk.END, " RESPOSTA DA IA\n", 'header')
                self.txt_ai.insert(tk.END, "="*100 + "\n\n", 'divider')
                self.txt_ai.insert(tk.END, resultado['resposta'], 'full')
                
                if '❌' in resultado['resposta']:
                    self.txt_ai.insert(tk.END, "\n\n DICA: Verifique se:\n", 'label')
                    self.txt_ai.insert(tk.END, "• Sua API Key está correta\n", 'full')
                    self.txt_ai.insert(tk.END, "• Você tem conexão com internet\n", 'full')
                    self.txt_ai.insert(tk.END, "• A pergunta foi capturada corretamente\n", 'full')
            
            # Configurar formatação
            self.txt_ai.tag_config('header', font=('Arial', 16, 'bold'), foreground='#1B5E20', background='#E8F5E9')
            self.txt_ai.tag_config('divider', foreground='#BDBDBD')
            self.txt_ai.tag_config('label', font=('Arial', 11, 'bold'), foreground='#0D47A1')
            self.txt_ai.tag_config('answer', font=('Arial', 24, 'bold'), foreground='#D32F2F', background='#FFEBEE')
            self.txt_ai.tag_config('explanation', font=('Arial', 11), foreground='#424242')
            self.txt_ai.tag_config('full', font=('Arial', 10), foreground='#616161')
            
            self.notebook.select(0)
            self.set_status("✓ IA respondeu!")
            
        except Exception as e:
            self.txt_ai.delete('1.0', tk.END)
            self.txt_ai.insert(tk.END, f"❌ ERRO AO CONSULTAR IA\n\n", 'header')
            self.txt_ai.insert(tk.END, f"Detalhes: {str(e)}\n\n", 'full')
            self.txt_ai.insert(tk.END, "Possíveis soluções:\n", 'label')
            self.txt_ai.insert(tk.END, "1. Verifique sua conexão com internet\n", 'full')
            self.txt_ai.insert(tk.END, "2. Confirme se a API Key está correta\n", 'full')
            self.txt_ai.insert(tk.END, "3. Tente novamente em alguns segundos\n", 'full')
            self.set_status("❌ Erro ao consultar IA")

    def copy_ai_response(self):
        if self.last_ai_response:
            texto = f"RESPOSTA: {self.last_ai_response.get('alternativa', 'N/A')}\n\n"
            texto += f"EXPLICAÇÃO:\n{self.last_ai_response.get('explicacao', '')}"
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            self.set_status("✓ Resposta copiada!")
        else:
            messagebox.showinfo("Info", "Nenhuma resposta para copiar!")

    def save_screenshot(self):
        if self.last_screenshot:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
            )
            if filename:
                self.last_screenshot.save(filename)
                self.set_status(f" Salvo: {os.path.basename(filename)}")
        else:
            messagebox.showinfo("Info", "Capture algo primeiro!")

    def clear_all(self):
        self.txt_ai.delete('1.0', tk.END)
        self.txt_ocr.delete('1.0', tk.END)
        self.last_text = ""
        self.last_screenshot = None
        self.last_ai_response = None
        self.set_status("✓ Limpo")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyApp(root)
    root.mainloop()
