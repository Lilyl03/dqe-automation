import os
import time
import csv
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class SeleniumWebDriverContextManager:
    def __enter__(self):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1400,1000")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
        return self.driver

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()


def wait_for(driver, xpath, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )


def extract_table(driver, outfile):
    table = wait_for(driver, "//*[@class='table']")
    columns = table.find_elements(By.CSS_SELECTOR, "g.y-column")
    columns_dict = {}

    for column in columns:
        header = column.find_elements(By.CSS_SELECTOR, "g.column-block#header")[0].text
        cells_list = []
        column_blocks = column.find_elements(By.CSS_SELECTOR, "g.column-block[id^='cells']")
        for column_block in column_blocks:
            column_cells = column_block.find_elements(By.CLASS_NAME, "column-cell")
            for column_cell in column_cells:
                cells_list.append(column_cell.text)
        columns_dict[header] = cells_list

    df = pd.DataFrame(columns_dict)
    df.to_csv(outfile, index=False, encoding="utf-8")


def get_pie(driver):
    layer = wait_for(driver, "//*[@class='trace']")
    texts = layer.find_elements(By.XPATH, ".//*[name()='text' and @class='slicetext']")
    out = []
    for t in texts:
        lines = t.find_elements(By.CSS_SELECTOR, "tspan.line")
        vals = [x.text for x in lines]
        out.append(vals)
    return out


def save_pie_csv(data, path):
    df = pd.DataFrame(data, columns=["Facility Type", "Min Average Time Spent"])
    df.to_csv(path, index=False, encoding="utf-8")


def pie_interaction(driver, outdir):
    os.makedirs(outdir, exist_ok=True)
    idx = 0

    driver.save_screenshot(f"{outdir}/screenshot{idx}.png")
    save_pie_csv(get_pie(driver), f"{outdir}/doughnut{idx}.csv")

    legend = driver.find_elements(By.CSS_SELECTOR, "g.legend .traces, g.traces")

    for i in range(min(4, len(legend))):
        try:
            legend[i].click()
            time.sleep(0.5)
            idx += 1
            driver.save_screenshot(f"{outdir}/screenshot{idx}.png")
            save_pie_csv(get_pie(driver), f"{outdir}/doughnut{idx}.csv")
            legend[i].click()
            time.sleep(0.5)
        except:
            pass


if __name__ == "__main__":
    path = os.path.abspath("report.html")

    with SeleniumWebDriverContextManager() as driver:
        driver.get(f"file:///{path}")
        extract_table(driver, "table.csv")
        pie_interaction(driver, "doughnut")