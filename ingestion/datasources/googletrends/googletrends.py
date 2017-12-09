# Basics
import numpy as np
import pandas as pd
import os

# Browser emulation
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# Custom
from ingestion import datasource as ds
from ingestion import database as db


url = r'https://trends.google.com/trends/explore?q=BTC'
gecko = os.path.normpath('.\ingestion\datasources\googletrends\geckodriver')

profile = webdriver.FirefoxProfile()
path = r'.\ingestion\datasources\googletrends'
profile.set_preference("browser.download.dir", r'.\ingestion\datasources\googletrends')
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
profile.set_preference("browser.download.folderList",2)

# profile.set_preference("browser.download.manager.showWhenStarting", False)
# profile.set_preference("browser.download.folderList", 2);
# profile.set_preference("browser.download.dir", path);
# profile.set_preference("browser.download.alertOnEXEOpen", False);
# profile.set_preference("browser.helperApps.neverAsksaveToDisk", "application/x-msexcel,application/excel,application/x-excel,application/excel,application/x-excel,application/excel,application/vnd.ms-excel,application/x-excel,application/x-msexcel");
# profile.set_preference("browser.download.manager.showWhenStarting", False);
# profile.set_preference("browser.download.manager.focusWhenStarting", False);
# profile.set_preference("browser.helperApps.alwaysAsk.force", False);
# profile.set_preference("browser.download.manager.alertOnEXEOpen", False);
# profile.set_preference("browser.download.manager.closeWhenDone", False);
# profile.set_preference("browser.download.manager.showAlertOnComplete", False);
# profile.set_preference("browser.download.manager.useWindow", False);
# profile.set_preference("browser.download.manager.showWhenStarting", False);
# profile.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False);
# profile.set_preference("pdfjs.disabled", True);


browser = webdriver.Firefox(firefox_profile=profile, executable_path = gecko + '.exe')
browser.get(url)
browser.find_element_by_xpath(r"/html[1]/body[1]/div[2]/div[2]/div[1]/md-content"+
                                r"[1]/div[1]/div[1]/div[1]/trends-widget[1]/ng-include[1]/"+
                                r"widget[1]/div[1]/div[1]/div[1]/widget-actions[1]/div[1]/button[1]").click()
