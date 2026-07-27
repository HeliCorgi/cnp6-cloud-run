# CNP6をGitHub Actionsで動かす — 最短手順

難しい設定は不要です。必要なのは次だけです。

1. GitHubで空の**公開**リポジトリを1個作る
2. このZIPを展開する
3. PowerShellに1行貼り付けてGitHubへ送る
4. GitHubのActions画面で`Run workflow`を押す
5. 完了後に結果ZIPをダウンロードする

## 1. 空の公開リポジトリを作る

GitHub右上の`+` → `New repository`。

- Repository name: `cnp6-cloud-run`
- Publicを選択
- README、.gitignore、Licenseは追加しない
- `Create repository`を押す

作成後、緑色の`Code`を押し、HTTPSのURLをコピーします。
例：

```text
https://github.com/あなたの名前/cnp6-cloud-run.git
```

## 2. ZIPを展開する

`CNP6_GITHUB_ACTIONS_READY.zip`を右クリックし、`すべて展開`。

展開後のフォルダを開きます。中に次があれば正解です。

- `UPLOAD_TO_GITHUB.ps1`
- `.github`
- `current`
- `cloud`

## 3. PowerShellでアップロードする

フォルダの何もない場所でShiftを押しながら右クリックし、`ターミナルで開く`または`PowerShellをここで開く`。

次を貼り付けます。URLだけ自分のものへ置き換えます。

```powershell
powershell -ExecutionPolicy Bypass -File .\UPLOAD_TO_GITHUB.ps1 -RepoUrl "https://github.com/あなたの名前/cnp6-cloud-run.git"
```

Gitが未導入なら自動インストールします。その場合はいったんPowerShellを閉じ、もう一度同じコマンドを実行します。

ブラウザでGitHubログイン許可が出たら許可します。

## 4. 計算を開始する

GitHubのリポジトリ画面で：

1. 上の`Actions`
2. 左の`CNP6 Step 31 Cloud`
3. 右の`Run workflow`
4. 最初は`quick`
5. `seed_offset`は`0`
6. 緑色の`Run workflow`

モデル生成10台、候補走査10台、彩色探索8台へ自動分割されます。

## 5. 結果を取る

実行画面が終わったら一番下の`Artifacts`にある

```text
CNP6-step31-result
```

を押します。ZIPがダウンロードされます。

そのZIPをChatGPTへアップロードすれば、次のstepから引き継げます。

## 赤い×が出た場合

まず同じworkflowを次の設定で再実行します。

- mode: `quick`
- seed_offset: 前回が0なら1、次は2

赤い×でも途中のArtifactsが残る場合があります。`CNP6-step31-result`があれば、それを優先して保存してください。

## 表示される結果の意味

- `5-SAT`：step31にも5彩色が見つかった。研究を次段へ続ける。
- `UNKNOWN`：設定時間内に5彩色が見つからなかっただけ。6色下界の証明ではない。
- `NO_COMMON_KILLERS`：今回作ったモデル群すべてを破る候補が足りない。`normal`または別の`seed_offset`で再実行する。

`UNKNOWN`を`UNSAT`や証明として扱わないでください。
