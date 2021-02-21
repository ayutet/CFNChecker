# CFNChecker
ストリートファイター5のオンラインステータスをDiscordに通知する
  Notify Discord of the online status of "Street Fighter 5"

CFNのMylistに登録したユーザ一覧から対象ユーザを探してONLINE状態・OFFLINE状態が切り替わったタイミングでWebHookを使用してDiscordに通知します。
Mylistを使用せずに対象ユーザのプロフィールページにアクセスして個々に状態をチェックするパターンも用意しましたが通信量が増えるのでお勧めしません。

推奨動作環境 Raspberry Pi4 ModelB
必要モジュール selenium / chromiumdriver / BeautifulSoup4 を別途インストールしてください
 >pip3 install selenium
 >sudo apt-get install chromium-chromedriver
 >pip install beautifulsoup4
 
注意事項
PC版のみ使用している場合、初回のSteam認証でメール送信による２段階認証が行われますがここは自動化できないので自分で入力してください。

初回起動後にログインが完了したらブラウザに「chrome://version/」と入力して「Profile Path」欄をコピーして環境設定に設定することで
次回起動時に前回のログイン情報を引き継ぐのでログイン処理が省略できます。
