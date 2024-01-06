import tkinter as tk
from tkinter import filedialog
import subprocess

def crawl():
    global category_entry
    global output_dir
    # 魔力赏市集位置 https://mall.bilibili.com/neul-next/index.html?page=magic-market_index
    from time import sleep  # 导入睡眠
    import requests
    import json
    import pandas as pd  # 导入pandas库
    import os
    from datetime import datetime

    url = "https://mall.bilibili.com/mall-magic-c/internet/c2c/v2/list"
    category_entry_value = category_entry.get()
    category_entry_a = category_entry_value.replace("c", "C")

    setprice = "{}-{}".format(int(float(min_price_entry.get()) * 100), int(float(max_price_entry.get()) * 100)) # 将最低价格和最高价格乘以100，并格式化为字符串
    discount = "{}-{}".format(int(min_discount_entry.get()), int(max_discount_entry.get()))  # 将最低折扣和最高折扣格式化为字符串，导入

    id_mapping = {
        '3C': '2273',
        '模型': '2066',
        '周边': '2331',
        '手办': '2312',
        '福袋': 'fudai_cate_id'  # 手办2312 模型2066 周边2331 3C2273 福袋fudai_cate_id
    }  # 创建一个字典，存储ID与名称的映射关系 用来文件名里ID部分的对应
    ID = id_mapping.get(category_entry_a, "Unknown")  # 根据分类 ID 获取对应的分类名称，未找到则返回 "Unknown"
    i_want = []
    nextId = None
    # 定义名称

    while True:  # 循环
        payload = json.dumps({
            "sortType": "PRICE_ASC",
            "priceFilters": [
                str(setprice)
            ],
            "discountFilters": [
                str(discount)
            ],
            "categoryFilter": str(ID),
            "nextId": nextId
        })
        headers = {
            'authority': 'mall.bilibili.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'content-type': 'application/json',
            'cookie':"自己输入",
            'origin': 'https://mall.bilibili.com',
            'referer': 'https://mall.bilibili.com/neul-next/index.html?page=magic-market_index',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            response = response.json()
            nextId = response["data"]["nextId"]  # 提取进入下一页所需的密钥

            if nextId is None:  # 没有下一页退出循环
                break

            for item in response["data"]["data"]:  # 遍历 'data' 列表中的每个商品信息
                # 提取每个商品的相关信息
                c2cItemsId = item["c2cItemsId"]  # 商品地址
                c2cItemsName = item["c2cItemsName"]  # 商品名称
                price = item["showPrice"]  # 价格（单位：元）
                showMarketPrice = item["showMarketPrice"]  # 市场价格

                # 将这些信息存储在一个字典中，并添加到 i_want 列表中
                i_want.append({
                    "c2cItemsName": c2cItemsName,
                    "c2cItemsId": c2cItemsId,
                    "price": price,
                    "showMarketPrice": showMarketPrice,
                })
        except Exception as e:  # 检测到操作频繁错误进入睡眠
            sleep(30)  # 睡眠30秒

    output_dir = filedialog.askdirectory()  # 输出文件的目录
    current_time = datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒")  # 获取当前时间并格式化
    file_name = f"{min_price_entry.get()}-{max_price_entry.get()}元{int(min_discount_entry.get()) // 10}-{int(max_discount_entry.get()) // 10}折{category_entry_a}_{current_time}.xlsx"  # 添加价格，折扣，品类，时间到文件名中
    output_file = os.path.join(output_dir, file_name)  # 构建完整的文件路径

    df = pd.DataFrame(i_want, columns=['c2cItemsName', 'c2cItemsId', 'price', 'showMarketPrice'])
    df.to_excel(output_file, index=False)  # 输出Excel
    print("商品信息已保存到：", output_file)

    pass

def select_output_dir():
    global output_dir
    output_dir = filedialog.askdirectory()

window = tk.Tk()
window.title("B站魔力赏市集商品信息爬取器")
window.geometry("600x400")

# 最低价格标签和输入框
min_price_label = tk.Label(window, text="最低价格")
min_price_label.pack()

min_price_entry = tk.Entry(window)
min_price_entry.pack()

# 最高价格标签和输入框
max_price_label = tk.Label(window, text="最高价格")
max_price_label.pack()

max_price_entry = tk.Entry(window)
max_price_entry.pack()

# 搜索品类标签和输入框
category_label = tk.Label(window, text="搜索品类（手办，模型，周边，3C，福袋）")
category_label.pack()

category_entry = tk.Entry(window)
category_entry.pack()

# 最低折扣标签和输入框
min_discount_label = tk.Label(window, text="最低折扣")
min_discount_label.pack()

min_discount_entry = tk.Entry(window)
min_discount_entry.pack()

# 最高折扣标签和输入框
max_discount_label = tk.Label(window, text="最高折扣（例如：70 最大100）")
max_discount_label.pack()

max_discount_entry = tk.Entry(window)
max_discount_entry.pack()


# 爬取按钮
crawl_button = tk.Button(window, text="开始爬取", command=crawl)
crawl_button.pack()

window.mainloop()