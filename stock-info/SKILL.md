---
name: stock-info
description: Monitor recent US, Taiwan and Korean market events (NASDAQ, S&P 500, SOX, KOSPI, Samsung/SK Hynix, CPI, Fed/FOMC, jobs data, TSMC/NVIDIA earnings, USD/TWD, USD/KRW, geopolitics, etc.) and evaluate their impact on the Taiwan stock market (TAIEX), summarized in about 300 Chinese characters. If the user then says "explain more detail" / 詳細說明 / 說詳細一點, produce a deeper survey. Use when the user asks about stock market news, 台股, 美股, 韓股, KOSPI, or invokes /stock-info.
allowed-tools: WebSearch, WebFetch
---

# Stock Info — 美股 / 台股 / 韓股事件監測與台股評估

Answer in Traditional Chinese (zh-TW). Tickers, index names and technical terms may stay in English.

## Step 1 — Get today's date and gather fresh data

Use the current date from context. Run several `WebSearch` calls **in the same turn** (use `mode: "extended"` for this skill: the facts are time-sensitive). Search with explicit dates, e.g. "S&P 500 close <today's date>", not just "S&P 500 today". Cover:

1. **US indices** — latest close and % change of NASDAQ, S&P 500, Dow, Philadelphia Semiconductor (SOX); VIX.
2. **Key US stocks for Taiwan** — TSMC ADR (TSM), NVIDIA, Apple, AMD, other AI / semiconductor names with big moves.
3. **Macro data** — most recent CPI / PCE / non-farm payrolls / unemployment / GDP releases (actual vs. expected), and upcoming release dates this week.
4. **Fed** — latest FOMC decision, rate expectations (e.g. CME FedWatch), notable Fed speeches; US 10Y yield; DXY.
5. **Taiwan market** — TAIEX latest close and % change, **TAIEX futures (台指期, near-month TX) latest close / change / % change, including the night session (夜盤) after the US close**, 外資台指期未平倉淨空單 (net OI) if found, turnover, foreign investor (外資) net buy/sell, TSMC (2330) price, USD/TWD, Taiwan central bank news, Taiwan export orders / exports.
6. **Korean market** — KOSPI and KOSDAQ latest close and % change, Samsung Electronics and SK Hynix price / % change, foreign investor (외국인) net buy/sell on KOSPI (억원 / 조원), USD/KRW, and Samsung / SK Hynix earnings dates (memory peers of the Taiwan supply chain). Korea closes 14:30 Taipei time; before that, report the previous close and label intraday numbers as 盤中.
7. **Other big events** — tariffs / trade policy, export controls on chips, US–China / cross-strait tension, major earnings (TSMC monthly revenue and quarterly results), oil price, Japan/China markets if they moved sharply.

**三大法人 (institutional flows)** — get the TWSE primary data for the latest 3 trading days with `WebFetch` on `https://www.twse.com.tw/rwd/zh/fund/BFI82U?type=day&dayDate=<YYYYMMDD>&response=json` (元; divide by 1e8 for 億元; 自營商 = 自行買賣 + 避險; 外資自營商 is already in 自營商, not added to 合計). If that returns no data (holiday, not yet published, fetch fails), fall back to news (中央社, 經濟日報, 鉅亨網) and say which rows came from news. Also look for the month-to-date cumulative and streaks (e.g. 外資連 N 賣, 投信連 N 買).

Prefer primary or reputable sources: BLS, BEA, Federal Reserve, TWSE (twse.com.tw), Taiwan central bank (cbc.gov.tw), Reuters, Bloomberg, CNBC, WSJ, 鉅亨網 (cnyes), 經濟日報, 工商時報, MoneyDJ; for Korea: KRX (krx.co.kr), Yonhap, Korea Times, Korea Herald / Herald Business, Seoul Economic Daily, 뉴스핌 (Newspim). Use `WebFetch` on a source page when a search snippet is ambiguous.

## Step 2 — Verify (do not guess)

- Every number (index level, %, CPI value, rate, flow amount) must come from a search/fetch result in this turn, with its **date**. Never fill numbers from memory.
- Check the date of each source. If the newest data found is older than the latest trading day, say so explicitly (e.g. 「最新取得資料為 10/13 收盤」).
- If two sources disagree, use the primary source, or report both.
- If something cannot be confirmed, write 「未能確認」 and do not state it as fact. Do not invent forecasts, analyst quotes, or event dates.
- Clearly separate **facts** (reported data) from **your assessment** (inference).

## Step 3 — Default output: ~300-character summary

Total ≈ 300 Chinese characters (plus a short source list, not counted). Structure:

```
📅 資料日期:<date of newest data>

【指數變動】(a table, one row per index; the ~300-character count excludes it)
| 指數 | 日期 | 收盤 | 漲跌 | 漲跌幅 |
|---|---|---|---|---|
| Dow | 10/20 | 52,495.88 | +530 | 🔺 +1.02% |
| S&P 500 | … | … | … | … |
| Nasdaq | … | … | … | … |
| SOX | … | … | … | … |
| TSM ADR | … | … | … | … |
| 加權指數 | … | … | … | … |
| 台指期(日盤 / 夜盤) | … | … | … | … |
| USD/TWD | … | … | … | … |
| KOSPI | … | … | … | … |
| KOSDAQ | … | … | … | … |
| 三星電子 / SK 海力士 | … | … | … | … |
| USD/KRW | … | … | … | … |

【三大法人】(上市,億元;latest 3 trading days, newest first; excluded from the ~300-character count)
| 日期 | 外資及陸資 | 投信 | 自營商 | 合計 |
|---|---|---|---|---|
| 10/22 | 🔻 −816.57 | 🔺 +88.75 | 🔻 −273.78(自行 −37.16、避險 −236.62) | 🔻 −1,001.60 |
| … | … | … | … | … |
  - 1–2 bullets: streaks (外資連 N 賣 / 投信連 N 買), month-to-date cumulative, what drove the latest day

【韓股重點】1–2 bullets: 外資 net buy/sell on KOSPI, what drove it, and how it compares with Taiwan (e.g. 記憶體 vs. 晶圓代工, KRW vs. TWD)
【美股與總經重點】2–4 個最重要事件,每項附數字與日期(index numbers already in the table: don't repeat them here)
【對台股影響評估】
  多空等級:<1–10>/10(<標籤>)
  震盪等級:<1–10>/10(<標籤>)
  理由(半導體/AI 鏈、記憶體與韓股連動、外資、匯率、利率)
【近期觀察】接下來 1–2 週要注意的事件與日期

來源:<site — date>, ...
```

Formatting rules:

- Put every index / price variation in the 【指數變動】 table, not inline in prose. Use thousands separators, a sign on every change (+ / −), 🔺 for up and 🔻 for down (台股習慣:漲紅跌綠 — the emoji only shows direction). Cells that cannot be confirmed show 「未能確認」.
- Each section is a short bullet list with a **bold topic** at the start of each bullet (e.g. `- **Fed**:…`), one fact per bullet.

Rating scales (pick one level each; the reason must point to the data behind it):

| 等級 | 多空等級 | 震盪等級 |
|---|---|---|
| 1 | 極度偏空 | 極端震盪 |
| 2 | 強烈偏空 | 劇烈震盪 |
| 3 | 偏空 | 明顯震盪 |
| 4 | 略偏空 | 偏大震盪 |
| 5 | 中性偏空 | 中度震盪 |
| 6 | 中性偏多 | 中度偏小震盪 |
| 7 | 略偏多 | 輕度震盪 |
| 8 | 偏多 | 輕微震盪 |
| 9 | 強烈偏多 | 小幅波動 |
| 10 | 極度偏多 | 平穩 |

There is no exact-neutral level: pick 5 or 6 by which side the data leans.

End with one line: 「以上為資訊整理與推論,非投資建議。」

## Step 4 — "Explain more detail" mode

When the user asks for more detail after a summary (e.g. "explain more detail", 詳細說明, 再詳細一點), do additional searches and produce a longer report (roughly 1000–1500 characters) covering:

1. Each event: what happened, actual vs. expected, market reaction, with numbers and dates.
2. Transmission to Taiwan: SOX/TSM ADR → TAIEX electronics; Fed/yields/DXY → USD/TWD → foreign flows; sector-by-sector (半導體、AI 伺服器、金融、傳產、航運) where data supports it.
3. Taiwan market data: TAIEX and 台指期 (day + night session, 正逆價差) trend over the last week as a table, 三大法人 (外資/投信/自營商) flows over the last 5 trading days as a table (same columns as Step 3), margin balance (融資餘額) if found.
   Korean market: KOSPI / KOSDAQ trend over the last week as a table, KOSPI 外資 flows, Samsung / SK Hynix moves and earnings, USD/KRW; what it signals for Taiwan memory / AI names (南亞科、華邦電 etc.) and foreign flows into Asia tech.
4. Upcoming calendar (with dates): CPI, FOMC, payrolls, TSMC earnings / monthly revenue, Samsung / SK Hynix earnings, Bank of Korea meeting, Taiwan central bank meeting, major US tech earnings.
5. Scenario view: what would make it bullish vs. bearish — framed as conditions, not predictions. Restate the 多空等級 and 震盪等級 (same 1–10 scales as Step 3) and what would move each level up or down.
6. Full source list with dates.

The same Step 2 verification rules apply. Same disclaimer at the end.
