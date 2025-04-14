import customtkinter as ctk
from ui_nav import Navegation
import time

class mainUI:
    def __init__(self):
        self.nav = Navegation()
        self.current_index = 0
        self.selected_id = None
        self.selected_detail = ""
        self.selected_href = None
        self.total_ids = 0

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.opcoes_tpr = {
            "Última semana": "r604800",
            "Último mês": "r2592000",
            "Últimos 3 meses": "r7776000"
        }

        self.opcoes_exp = {
            "Estágio": "1", "Júnior": "2", "Pleno": "3", "Sênior": "4", "Diretoria": "5"
        }

        self.opcoes_tipo_trabalho = {
            "Presencial": "1", "Remoto": "2", "Híbrido": "3"
        }

        self.opcoes_tipo_vaga = {
            "Tempo integral": "F", "Meio período": "P", "Contrato": "C",
            "Temporário": "T", "Estágio": "I", "Voluntário": "V"
        }

        self.window = ctk.CTk()
        self.window.title("LinkedIn - Filtros de Vagas")
        self.window.geometry("500x500")

        self.entry_keywords = ctk.CTkEntry(self.window, placeholder_text="Palavra-chave", width=300)
        self.entry_keywords.pack(pady=6)

        self.combo_tpr = ctk.CTkComboBox(self.window, values=[""] + list(self.opcoes_tpr.keys()), width=300)
        self.combo_tpr.set("Período de publicação")
        self.combo_tpr.pack(pady=6)

        self.combo_exp = ctk.CTkComboBox(self.window, values=[""] + list(self.opcoes_exp.keys()), width=300)
        self.combo_exp.set("Experiência")
        self.combo_exp.pack(pady=6)

        self.combo_trabalho = ctk.CTkComboBox(self.window, values=[""] + list(self.opcoes_tipo_trabalho.keys()), width=300)
        self.combo_trabalho.set("Tipo de trabalho")
        self.combo_trabalho.pack(pady=6)

        self.combo_vaga = ctk.CTkComboBox(self.window, values=[""] + list(self.opcoes_tipo_vaga.keys()), width=300)
        self.combo_vaga.set("Tipo de vaga")
        self.combo_vaga.pack(pady=6)

        self.botao = ctk.CTkButton(self.window, text="✅ Pesquisar", command=self.abrir_url, width=300)
        self.botao.pack(pady=6)

        self.next_btn = ctk.CTkButton(self.window, text="➡️ Próximo ID", command=self.next_control_id, width=300)
        self.result_box = ctk.CTkTextbox(self.window, width=460, height=200)
        self.result_box.pack(pady=10)

        self.window.lift()
        self.window.attributes('-topmost', True)
        self.window.after(1000, lambda: self.window.attributes('-topmost', False))

    def gerar_url(self):
        base = "https://www.linkedin.com/jobs/search/?"
        params = []

        keywords = self.entry_keywords.get().strip().replace(" ", "%20")
        if keywords:
            params.append(f"keywords={keywords}")

        filtros = [
            (self.opcoes_tpr, self.combo_tpr, "f_TPR"),
            (self.opcoes_exp, self.combo_exp, "f_E"),
            (self.opcoes_tipo_trabalho, self.combo_trabalho, "f_WT"),
            (self.opcoes_tipo_vaga, self.combo_vaga, "f_JT"),
        ]

        for opcoes, combo, nome in filtros:
            valor = opcoes.get(combo.get(), "")
            if valor:
                params.append(f"{nome}={valor}")

        return base + "&".join(params)

    def abrir_url(self):
        url = self.gerar_url()
        self.selected_id, self.selected_detail, self.selected_href, self.current_index = self.nav.read_body(url)
        self.total_ids = 1 if self.current_index is not None else 0
        self.show_control_id()
        self.next_btn.pack(pady=6)  # Só exibe após buscar

    def show_control_id(self):
        self.result_box.delete("1.0", "end")
        if self.selected_id:
            self.result_box.insert("end", f"🔹 ID:\n{self.selected_id}\n\n📝 Descrição:\n{self.selected_detail}")
        else:
            self.result_box.insert("end", "❌ Nenhum ID encontrado.")

    def next_control_id(self):
        if self.selected_id is not None and self.current_index is not None:
            next_index = self.current_index + 1
            human_card = next_index + 1

            if human_card % 6 == 0:
                self.nav.scroll_next_block()

            script = f"""
                let items = document.querySelectorAll('[data-control-id]');
                if ({next_index} < 25) {{
                    items[{next_index}].click();
                }} else {{
                    throw new Error("No more items");
                }}
            """
            try:
                self.nav.driver.execute_script(script)
                time.sleep(1)  # tempo para a vaga carregar
                self.selected_id, self.selected_detail, self.selected_href, self.current_index = self.nav.read_body()
                self.show_control_id()
            except Exception as e:
                self.result_box.delete("1.0", "end")
                self.result_box.insert("end", "🔚 Fim das vagas.")
        else:
            self.result_box.delete("1.0", "end")
            self.result_box.insert("end", "🔚 Fim das vagas.")

    def mostrar(self):
        self.window.mainloop()
