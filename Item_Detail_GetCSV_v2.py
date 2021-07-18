

import ssl
import time
import requests
import json
import pandas as pd
from urllib.parse import quote


#使用者可輸入想搜尋的關鍵字
print('請輸入您想搜尋的關鍵字：')
search_keyword = input()


#將關鍵字編碼
search_keyword = quote(search_keyword)

# only to get id from the front page
def parseWholeCategory():  

    itemid = []
    shopid = []

    base_url = 'https://shopee.tw/api/v4/search/search_items'
    for batch in range(20):
        query = f"?by=relevancy&keyword={search_keyword}&limit=50&newest={batch*50}&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
        #print(query)
        url = base_url + query
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'referer': f'https://shopee.tw/search?keyword={search_keyword}',  #urllib.parse.unquote(url)後發現就是瀏覽器上的網址
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-api-source': 'pc',
            'x-requested-with': 'XMLHttpRequest'
        }

        #下載網頁存於'r'之中
        s = requests.Session()
        r = s.get(url, headers=headers)

        #使用判斷是檢查網頁狀態碼
        if r.status_code == requests.codes.ok:
            data = r.json()
            data = data["items"]
        for item in data:  
            trans = json.dumps(item)
            extracted_data_json = json.loads(trans)  # loads takes str
            itemid.append(extracted_data_json['itemid'])  # itemid
            shopid.append(extracted_data_json['shopid'])  # shopid
        time.sleep(3) 
    id_list = [itemid, shopid]
    return id_list

#===============================================================================================================================
# use id list to get each detail
def parseItems(id_list):
    ssl._create_default_https_context = ssl._create_unverified_context
    #商品詳細資訊
    name = []
    itemid_l = []
    shopid_l = []
    historical_sold = []
    sold = []
    models = [] 
    item_rating = []
    description_l = []
    rating = []

    # print(f'id_list = {id_list} ')
    for i in range(id_list[0]):
        itemid = id_list[0][i]
        shopid = id_list[1][i]
        #print(f'itemid = {itemid} ')
        #print(f'shopid = {shopid} ')
        url= f'https://shopee.tw/api/v2/item/get?itemid={itemid}&shopid={shopid}'



    # --------- another file about description ---------
    # 另存一個檔案專抓商品描述和評論 用以下標籤  
    # 評論要送另一個request
        # name
        # description
        # categories
        # item_rating['rating_star']

        headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            # 'referer': f'https://shopee.tw/api/v2/item/get?itemid={itemid}&shopid={shopid}',  #urllib.parse.unquote(url)後發現就是瀏覽器上的網址 
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-api-source': 'pc',
            'x-requested-with': 'XMLHttpRequest'
        }

        #反反爬蟲用途
        proxie = { 
                'http': 'http://122.193.14.102:80'
        }   


        # reload(sys)
        s = requests.Session()
        r = s.get(url, verify=False, proxies = proxie, headers=headers,timeout = 20, allow_redirects=False)
        #print(url)
        if r.status_code == requests.codes.ok:
            data = r.json()
            extracted_data_json = data['item']
        else:
            print('something wrong!')

        name.append(extracted_data_json['name']) #商品名稱
        itemid_l.append(extracted_data_json['itemid'])  # itemid
        shopid_l.append(extracted_data_json['shopid'])  # shopid
        historical_sold.append(extracted_data_json['historical_sold']) #已售出數量
        sold.append(extracted_data_json['sold'])
        models.append(extracted_data_json['models'][0]['price'])  #models[0]['price']
        item_rating.append(extracted_data_json['item_rating']['rating_star']) #item_rating['rating_star']
        description_l.append(extracted_data_json['description'])
        rating.append(extracted_data_json['item_rating']['rating_count'][0])
            # ----------- If JSON file's needed -------------
            # with open('ItemDescrip.json', "a+") as f:   
            #     trans = json.dumps(data, indent=4)  
            #     f.write(trans)    # f.write(data.text)

    data_dic = {'name':name,'itemid':itemid_l, 'shopid':shopid_l, 'historical_sold':historical_sold, 'sold':sold, 'models':models, 'item_rating':item_rating, 'description':description_l }
    df = pd.DataFrame.from_dict( data_dic )
    df.to_csv('ItemDetail.csv',encoding='utf-8')
    time.sleep(2)
    return rating


def parseFeedback(id_list, rating):
    ssl._create_default_https_context = ssl._create_unverified_context

    #回饋資訊
    shopid_u = []
    description_u = []
    kind = []
    rating_star = []
    for i in range(1):
        itemid = id_list[0][i]
        shopid = id_list[1][i]
        rating = int(rating[i]/6)


        for j in range(rating):

            url= f'https://shopee.tw/api/v2/item/get_ratings?filter=0&flag=1&itemid={itemid}&limit=6&offset={j*6}&shopid={shopid}&type=0'

        headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            # 'referer': f'https://shopee.tw/api/v2/item/get?itemid={itemid}&shopid={shopid}',  #urllib.parse.unquote(url)後發現就是瀏覽器上的網址
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-api-source': 'pc',
            'x-requested-with': 'XMLHttpRequest'
        }

    #反反爬蟲用途
        proxie = {
            'http': 'http://122.193.14.102:80'
        }

        s = requests.Session()
        r = s.get(url, verify=False, proxies = proxie, headers=headers,timeout = 20, allow_redirects=False)
        time.sleep(2)
        if r.status_code == requests.codes.ok:
            data = r.json()
            extracted_data_json = data['data']['ratings']
        else:
            print('something wrong!')


        for k in extracted_data_json:
            shopid_u.append(k['author_shopid'])
            description_u.append(k['comment'])
            kind.append(k['product_items'][0]['model_name'])
            rating_star.append(k['rating_star'])

        data_dic = {'shopid':shopid_u,'description': description_u, 'kind':kind, 'rating_star':rating_star}
        df = pd.DataFrame.from_dict( data_dic )
        df.to_csv(f'../hellogit/{itemid}.csv',encoding='utf-8')
        time.sleep(2)


parseFeedback(parseWholeCategory(), parseItems(parseWholeCategory()))
