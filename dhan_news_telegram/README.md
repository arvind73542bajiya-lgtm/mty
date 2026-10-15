# Dhan News → Telegram (Mobile)

Ye bot Dhan API se news headlines laata hai aur nayi headlines aapke mobile par
**Telegram message** ki tarah bhejta hai. Koi extra library install nahi karni.
Sirf Python 3 chahiye.

## Step 1: Telegram bot banao
1. Telegram mein **@BotFather** kholo aur `/newbot` bhejo.
2. Naam do. BotFather ek **token** dega, jaise `123456789:ABC...`.
3. Apne naye bot ko kholo aur **/start** bhejo.

## Step 2: Dhan details
1. web.dhan.co → Profile → **DhanHQ Trading APIs** se **Access Token** banao.
   Wahi se apna **Client ID** bhi lo.
2. Browser mein https://api.dhan.co/v2/ kholo aur **News Headline** wala section dekho.
   Wahan se ye 3 cheezein lo:
   - endpoint ka **path** (jaise `/v2/...`)
   - method: **GET** ya **POST**
   - request mein kya bhejna hai (NewsHeadlineRequest ke fields)

## Step 3: config.json bharo
```
cp config.example.json config.json
```
`config.json` kholo aur bharo:
| Field | Kya dalna hai |
|---|---|
| `dhan_client_id` | Dhan Client ID |
| `dhan_access_token` | Dhan Access Token |
| `news_path` | Docs se news endpoint ka path |
| `news_method` | `GET` ya `POST` |
| `news_request_body` | Docs ke NewsHeadlineRequest ke fields (POST ke liye) |
| `telegram_bot_token` | BotFather wala token |
| `telegram_chat_id` | Neeche wali command se milega |
| `poll_seconds` | Kitne second mein check kare (300 = 5 minute) |

Chat id pata karne ke liye:
```
python3 news_bot.py --chat-id
```

## Step 4: Test karo
```
python3 news_bot.py --test
```
Ye Dhan ka raw jawaab aur pehchaani gayi headlines dikhayega.
Agar error aaye to `news_path`, `news_method` aur `news_request_body` docs se
dobara milao.

```
python3 news_bot.py --once
```
Isse ek baar news check hogi aur Telegram par message aayega.

## Step 5: Lagatar chalao
```
python3 news_bot.py
```
Bot har 5 minute mein check karega aur sirf **nayi** headlines bhejega.
Bheji gayi news `seen_news.json` mein yaad rehti hai, isliye koi news dobara nahi aayegi.
Pehli baar chalane par sirf latest 5 headlines aayengi.

**Android par chalana ho to:** Play Store/F-Droid se **Termux** install karo, phir:
```
pkg install python git
git clone <is repo ka link>
cd mty/dhan_news_telegram
```
Uske baad Step 3 se shuru karo.

> Note: Dhan Access Token kuch samay baad expire hota hai (lagbhag 24 ghante).
> Expire hone par naya token banakar `config.json` mein badal do.
> `config.json` git mein commit nahi hoti, isliye aapka token safe rahega.
