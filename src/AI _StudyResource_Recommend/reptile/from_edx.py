import requests
from bs4 import BeautifulSoup
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 这是一个从edx上随机爬取若干课程的爬虫

def reptile_from_edx():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    target_url = 'https://www.edx.org/learn/artificial-intelligence'
    base_url = 'https://www.edx.org'
    driver.get(target_url)
    # 发送请求获取页面内容
    response = requests.get(target_url)
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析HTML内容
        html = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html, 'html.parser')
        target_a_tags = soup.findAll('a', {'class': 'base-card-link'})
        extracted_info = []

        # 遍历找到的a标签
        for tag in target_a_tags:
            if tag.has_attr('href'):  # 确保a标签有href属性
                href = base_url + tag['href']
                title_content = tag.find('div', {'class': 'pgn__card-header-title-md'})

                if title_content is not None:
                    # 将所有span标签中的文本连接起来，忽略换行
                    title_text = " ".join(title_content.get_text(separator=" ", strip=True).split())
                    extracted_info.append((href,title_text))


        # 检查是否成功提取了URL
        if extracted_info:
            selected_info = random.sample(extracted_info, min(3, len(extracted_info)))  # 随机选择3个或者少于3个的元素
            # 循环展示选中的内容
            for idx, (href, label) in enumerate(selected_info, start=1):
                print(f"提取到的第{idx}个学习网址:", href)
                print(f"标签:", label)
                data = {href, label}
                #TODO 存进数据库

    else:
        print("获取页面失败，状态码:", response.status_code)