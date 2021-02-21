# ======================================================================================
# Readme
# 動作環境 Raspberry Pi 4 ModelB
# 必要モジュール selenium / chromiumdriver / BeautifulSoup4 / 
# STEAM版ログインは２段階メール認証が無理なんでログイン手動で…
# MyList使用版はログインユーザのCFNで登録したユーザ一覧(1ページ100件)からチェック対象ユーザを探す
# Profile使用版はチェック対象ユーザのプロフィールページに飛ぶのでMyListに登録しなくても動作する
# 　※ただし、大量に登録するとページアクセスが多くなのでおすすめしない。
# ======================================================================================
# 2021/02/02 新規作成
# 2021/02/10 リファクタリング
# 2021/02/14 ユーザリスト100件超え対応(必要性は不明)
# 2021/02/19 MyList不使用版（各ユーザプロフィールページアクセスなのであまりお勧めしない）
# ==============================================================================
# ユーザの環境設定 (要設定)
# ==============================================================================
# チェックしたいユーザ(大文字小文字正確に) 例 ["user1", "user2", "user3"]
CheckUser = ["","",""]

# CFNのMyListを使用 / Falseの場合はユーザプロフィールから取得
CheckMyList = True
#CheckMyList = False

# CFNログイン PSN/STEAM選択 コメントアウト[#]で切り替え
LoginSite = "PSN"
#LoginSite = "STEAM" ２段階認証が無理なので そこは手動で

# ログインユーザ/パスワード
LoginUser = ""
LoginPassword = ""

# ChromiumのProfile Path
# アドレスバーに「chrome://version/」と入力して「Profile Path」と書かれているところをコピペ
profile_path = '/tmp/.org.chromium.Chromium.*******/Default'

# WebHookURLを設定
WebHookUrl = "https://discord.com/api/webhooks/***************************"

# WebHookでメッセージ送信するときのユーザ名
WebHookUser = "通知BOTちゃん"

# チェック間隔(秒) ※早すぎるとサーバに迷惑がかかるので注意
TimerInterval = 300

# Pythonの各種パッケージPath
Packages_Path = "/home/pi/.local/lib/python3.5/site-packages/"

# ChromiumドライバのPath
Chromium_Path = "/usr/lib/chromium-browser/chromedriver"

# ==============================================================================
# ユーザの環境設定終了 以後触る必要なし
# ==============================================================================

# ===============
# サーバ環境設定
# ===============
# PSNのログインページ
PSNLoginUrl = "https://game.capcom.com/cfn/sfv/consent/sen"

# STEAMのログインページ
STEAMLoginUrl = "https://game.capcom.com/cfn/sfv/consent/steam"

# CFN Mylistページ
CFNMypageUrl = "https://game.capcom.com/cfn/sfv/mylist"

# CFN ユーザプロフィールページ
CFNProfileUrl = "https://game.capcom.com/cfn/sfv/profile/"

# =================
# PSNログイン処理
# =================
def PSNLogin(browser):
    from time import sleep

    # ログインページ移動   
    browser.get(PSNLoginUrl) #PS版
    
    # 同意するボタンクリック
    browser.find_element_by_xpath("//input[@value='同意する']").click()
    sleep(10)

    # アカウント入力
    browser.find_element_by_xpath("//input[contains(@title,'サインインID')]").send_keys(LoginUser)
    sleep(1)

    # 次へクリック
    browser.find_element_by_class_name("primary-button").click()
    sleep(1)

    # パスワード入力
    browser.find_element_by_xpath("//input[contains(@title,'パスワード')]").send_keys(LoginPassword)
    sleep(1)

    # ログインクリック
    browser.find_element_by_class_name("primary-button").click()
    sleep(10)

# =================
# STEAMログイン処理
# =================
def STEAMLogin(browser):
    from time import sleep

    # ログインページ移動   
    browser.get(STEAMLoginUrl) #PS版

    # 同意するボタンクリック
    browser.find_element_by_xpath("//input[@value='同意する']").click()
    sleep(10)

    # アカウント入力
    browser.find_element_by_xpath("//input[contains(@id,'steamAccountName')]").send_keys(LoginUser)
    sleep(0.3)

    # パスワード入力
    browser.find_element_by_xpath("//input[contains(@id,'steamPassword')]").send_keys(LoginPassword)
    sleep(0.3)

    # ログインクリック
    browser.find_element_by_xpath("//input[contains(@id,'imageLogin')]").click()
    sleep(10)

# =================
# Discord送信処理
# =================
def SendDiscord(message):
    import requests

    # WebHookのURL
    params = {"username": WebHookUser,"content": message}
    # 送信！
    requests.post(WebHookUrl,params)

# =======================
# 状態保存とDiscord送信判定
# =======================
def StatusCheck(user,status):

    # 現在のステータスがオンラインかチェック
    if (status == "ONLINE"):

        # 前回ステータスがOFFLINEかチェック
        if (mylist[user] == "OFFLINE"):
            # 通知処理
            message = user + "さんがオンラインになりました。"
            SendDiscord(message)
                    
        # 状態保存
        mylist[user] = "ONLINE"

    else:
        # 前回のステタスがONLINEかチェック
        if (mylist[user] == "ONLINE"):
            print("通知")
            # 通知処理
            message = user + "さんがオフラインになりました。"
            SendDiscord(message)

        # 状態保存
        mylist[user] = "OFFLINE"

# =======================
# ページ解析処理MyList用
# =======================
def MyListPageAnalyzer(soup):

    # HTML解析 BeautifulSoup使用
    import requests
    from bs4 import BeautifulSoup
    #soup = BeautifulSoup(PageSource,"html.parser")

    # タグで切り出し
    import re
    member = soup.find('table', {'class': 'member'})

    # ユーザ名一覧取得(何故か先頭にスペース入ってる)
    users = member.find_all('td',{'class': 'name'})

    # オンラインステータつ取得 (タグが nowStattus ONLINE/OFFLINEで切り替わる)
    status = member.find_all('div',{'class': re.compile('nowStatus')})
    
    # ====================
    # 取得したデータをループ
    # ====================
    i = 0
    for item in users:
        # 予め前スペース抜きのユーザ名を格納
        checkuser = item.text.replace(" ","")

        # ユーザ名がチェック対象にあるか判定
        if (checkuser in mylist):
            # ステータスチェックにかける -> Discord送信
            StatusCheck(checkuser,status[i].text)

        i = i+1
    # ====================
    # ループ終わり
    # ====================

# =========================
# ページ解析処理Profile用
# =========================    
def ProfilePageAnalyzer(PageSource,user):

    # HTML解析 BeautifulSoup使用
    import requests
    from bs4 import BeautifulSoup
    # 解析用にBeutifulSoupに変換
    soup = BeautifulSoup(PageSource,"html.parser")

    # NowStatusタグを検索して状態取得
    import re
    status = soup.find('div',{'class': re.compile('nowStatus')}).text.replace('\n','')

    # ステータスチェックにかける -> Discord送信
    StatusCheck(user,status)

# =====================
# CFN MyListチェック処理
# =====================
def MylistCheck(browser):
    # HTML解析 BeautifulSoup使用
    import requests
    from bs4 import BeautifulSoup

    # MyPageを取得
    browser.get(CFNMypageUrl)
    PageSource = browser.page_source
    
    # 解析用にBeutifulSoupに変換
    soup = BeautifulSoup(PageSource,"html.parser")
    # 解析処理に渡す(MyList用)
    MyListPageAnalyzer(soup)

    # 改ページ処理(100人以上いれば…)必要か？
    while True:
        nextUrl = soup.find('p', {'class': 'next'}).find('a').get('href')
        if (nextUrl is not None):
            # 次ページに移動してソースを取得
            browser.get(nextUrl)
            PageSource = browser.page_source
            # 解析用にBeutifulSoupに変換
            soup = BeautifulSoup(PageSource,"html.parser")
            # 解析処理に渡す(MyList用)
            MyListPageAnalyzer(soup)
        else:
            break

# =====================
# CFN Profileチェック処理
# =====================
def ProfileCheck(browser):
    from time import sleep

    # HTML解析 BeautifulSoup使用
    import requests
    from bs4 import BeautifulSoup

    # チェックユーザ毎にプロフィールページにアクセス
    for user in CheckUser:
        print(user)
        # Profileページを取得 URL:基礎＋ユーザ名
        browser.get(CFNProfileUrl + user)
        PageSource = browser.page_source

        # 解析処理に渡す(プロフィール用)
        ProfilePageAnalyzer(PageSource,user)

# =============================
# メイン処理
# =============================
# チェック対象ユーザのディクショナリ作成
mylist = {}
for item in CheckUser:
    mylist[item] = ""

# ブラウザの準備
# オプション：ブラウザのログイン情報を引き継ぐためユーザ設定
# オプション：ブラウザの言語設定を日本語に
import sys
sys.path.append(Packages_Path)
from selenium import webdriver
option = webdriver.ChromeOptions()
option.add_argument('--user-data-dir=' + profile_path)
option.add_experimental_option('prefs',{'intl.accept_languages':'ja-JP'})
browser = webdriver.Chrome(executable_path=Chromium_Path,options=option)

# MyList移動
browser.get(CFNMypageUrl)

from time import sleep
sleep(10)

# ==============================
# ログイン済み判定・ログイン処理
# ==============================
#現在のURLを取得（Cookie情報がないとTOPに飛ばされている）
if (CFNMypageUrl != browser.current_url):
    # ログインが必要なのでログイン処理
    if (LoginSite == "PSN"):
        #PSNでログイン
        PSNLogin(browser)
    else:
        #STEAMでログイン
        STEAMLogin(browser)

    browser.get(CFNMypageUrl)
    sleep(10)

# ==============================
# タイマーループ(永遠)
# ==============================
while True:
    try:
        if (CheckMyList):
            MylistCheck(browser)
        else:
            ProfileCheck(browser)

        sleep(TimerInterval)

    except:
        # 時間をおいてリトライ
        sleep(TimerInterval)

# ==============================
