### Money Transfer

**Objetive:** Build an automated simple program that converts from MXN to EUR using XRP as an itermediate

The steps the program will follow are

1. Convert Fiat MXN to XRP using Bitso API (XRP/MXN) placing a limit order at top of the sell orderbook so the transaction goes immediately

2. Withdraw from Bitso onto Binance the XRP

3. When the withdraw is approved convert to EUR placing limit order at top of buying orderboo, (XRP/EUR)

4. Withdraw EUR to european bank account from Binance

   **Remarks:** Give a clear breakdown of the fees involved in the process and in turn the final exchange rate achived by the program, as there is a withdrawal fee from Binance for EUR it's clear than the higher the ammount of money involved in the operation then the better exchange rate.