# GMO Coin Buy

GMOコインでビットコインを買うためのスクリプト

## 事前準備
### Pythonをインストール
3.8.5を使って開発しました。f文字列を使っているので、バージョン3.6以上が必要です。

### パッケージをインストール

```
$ pip install -r requirements.txt
```

### 設定ファイル
サンプルのconfigをコピーする

```bash
$ cp config.json.example config.json
```

次に、`config.json`を編集する

* setting
  * endpoint: エンドポイントのURL
  * symbols: 取引所で有効な通貨コードのリスト
  * minamount: 各銘柄の最低取引単位
* order
  * targetsymbol: 購入する銘柄の通貨コード
  * budget: 1回の注文で支払う金額の上限 (円)

### 環境変数
APIキーとAPIシークレットをexportする

```bash
$ source export_env.sh
API Key: (APIキーを入力する)
API Secret: (APIシークレットを入力する)
```

シェルの種類によっては動作しない可能性があるので、その際はこのスクリプトを使わずに自分で設定してください

## 実行
```bash
$ python main.py
```

## 後処理
使わなくなったら、環境変数に登録したAPIキーとAPIシークレットを削除しておきましょう

```bash
$ source unset_env.sh
```

シェルの種類によっては動作しない可能性があるので、その際はこのスクリプトを使わずに自分で削除してください