from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import customtkinter as ctk
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class Navegation:
    def __init__(self):
        self.driver = None
        self.options = Options()
        self.options.add_argument("--start-maximized")

    def abrir_navegador(self):
        if self.driver is None:
            self.driver = webdriver.Chrome(options=self.options)

    def fazer_login(self):
        with open("credential.txt", "r") as file:
            login = file.readline().strip()
            senha = file.readline().strip()

        self.driver.get("https://www.linkedin.com/login")
        self.driver.find_element(By.ID, "username").send_keys(login)
        self.driver.find_element(By.ID, "password").send_keys(senha)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(2)

        if "checkpoint/challenge" in self.driver.current_url:
            input("✉️ Código de verificação enviado. Pressione ENTER após login...")
            time.sleep(1)

    def navigation(self, url):
        self.abrir_navegador()
        if "login" in self.driver.current_url or self.driver.current_url == "data:,":
            self.fazer_login()
        self.driver.get(url)
    
    def scroll_slowly(self, container, total=837, steps=6, delay=0.35):
        step = total // steps
        for _ in range(steps):
            self.driver.execute_script(f"arguments[0].scrollTop += {step};", container)
            time.sleep(delay)

    def scroll_next_block(self):

        try:
            job_card = self.driver.find_element(By.CSS_SELECTOR, "li[data-occludable-job-id]")
            ul_element = job_card.find_element(By.XPATH, "./ancestor::ul[1]")
            scroll_container = ul_element.find_element(By.XPATH, "./parent::div")
            print(f"✅ Container localizado: tag={scroll_container.tag_name}, class={scroll_container.get_attribute('class')}")
        except Exception as e:
            print(f"❌ Erro ao localizar scroll container: {e}")
            return
        self.scroll_slowly(scroll_container)
        time.sleep(1.67)
        return


    def read_body(self, url=None):
        if url:
            self.navigation(url)

        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "li[data-occludable-job-id]")) >= 25
            )
        except:
            print("⚠️ job-details não apareceu a tempo.")

        # Lê o conteúdo atual renderizado
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        list_div = soup.find("div", class_="scaffold-layout__list")
        detail_div = soup.find("div", class_="scaffold-layout__detail")

        selected_detail = ""
        selected_id = None
        selected_href = None
        current_index = None

        # Extrai o ID e detalhe do card atual
        if detail_div:
            selected_a = detail_div.find("a", attrs={"data-control-id": True})
            if selected_a:
                selected_id = selected_a.get("data-control-id")
                details = detail_div.find("div", id="job-details")
                selected_detail = details.get_text(strip=True) if details else ""

        # Associa o ID atual ao índice e ao href
        if list_div and selected_id:
            list_items = list_div.find_all("a", attrs={"data-control-id": True})
            for idx, a in enumerate(list_items):
                if a.get("data-control-id") == selected_id:
                    href = a.get("href")
                    selected_href = f"https://www.linkedin.com{href}" if href else None
                    current_index = idx
                    break

        return selected_id, selected_detail, selected_href, current_index