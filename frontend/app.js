const compareBtn = document.getElementById("compare-btn");
const compareResult = document.getElementById("compare-result");
const compareError = document.getElementById("compare-error");

compareBtn.addEventListener("click", async () => {
  compareError.textContent = "";
  compareResult.innerHTML = "";

  const symbol = document.getElementById("symbol").value.trim();
  const investedAmount = parseFloat(document.getElementById("investedAmount").value);
  const buyDate = document.getElementById("buyDate").value;
  const sellDate = document.getElementById("sellDate").value || "";

  const purchasePrice = parseFloat(document.getElementById("purchasePrice").value);
  const downPaymentPercent = parseFloat(document.getElementById("downPaymentPercent").value);
  const annualInterestRate = parseFloat(document.getElementById("annualInterestRate").value);
  const reBuyDate = document.getElementById("reBuyDate").value;
  const asOfDate = document.getElementById("asOfDate").value;
  const annualAppreciationPercent = parseFloat(document.getElementById("annualAppreciationPercent").value) || 0;

  const params = new URLSearchParams();

  if (symbol && investedAmount > 0 && buyDate) {
    params.set("symbol", symbol);
    params.set("investedAmount", String(investedAmount));
    params.set("buyDate", buyDate);
    if (sellDate) params.set("sellDate", sellDate);
  }
  if (purchasePrice > 0 && downPaymentPercent != null && annualInterestRate != null && reBuyDate && asOfDate) {
    params.set("purchasePrice", String(purchasePrice));
    params.set("downPaymentPercent", String(downPaymentPercent));
    params.set("annualInterestRate", String(annualInterestRate));
    params.set("reBuyDate", reBuyDate);
    params.set("asOfDate", asOfDate);
    if (annualAppreciationPercent !== 0) params.set("annualAppreciationPercent", String(annualAppreciationPercent));
  }

  if (params.toString() === "") {
    compareError.textContent = "Fill in at least the stock section or the real estate section.";
    return;
  }

  compareBtn.disabled = true;
  try {
    const res = await fetch(`/api/compare?${params}`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Request failed");
    }
    renderCompareResult(data);
  } catch (err) {
    compareError.textContent = err.message;
  } finally {
    compareBtn.disabled = false;
  }
});

function renderCompareResult(data) {
  const stock = data.stock;
  const realEstate = data.realEstate;

  let html = '<div class="compare-columns">';
  if (stock) {
    const gainClass = stock.gainLoss >= 0 ? "positive" : "negative";
    html += `
      <div class="result-panel">
        <h3>Stocks: ${stock.symbol}</h3>
        <dl>
          <dt>Buy date</dt><dd>${stock.buyDate}</dd>
          <dt>Sell date</dt><dd>${stock.sellDate}</dd>
          <dt>Buy price (adj.)</dt><dd>$${stock.buyPrice.toFixed(2)}</dd>
          <dt>Sell price (adj.)</dt><dd>$${stock.sellPrice.toFixed(2)}</dd>
          <dt>Shares</dt><dd>${stock.shares.toFixed(4)}</dd>
          <dt>Cost basis</dt><dd>$${stock.costBasis.toFixed(2)}</dd>
          <dt>Value at sell</dt><dd>$${stock.valueAtSell.toFixed(2)}</dd>
          <dt>Gain / loss</dt><dd class="${gainClass}">$${stock.gainLoss.toFixed(2)} (${stock.gainLossPercent >= 0 ? "+" : ""}${stock.gainLossPercent.toFixed(2)}%)</dd>
        </dl>
      </div>
    `;
  }
  if (realEstate) {
    const gainClass = realEstate.gainLoss >= 0 ? "positive" : "negative";
    html += `
      <div class="result-panel">
        <h3>Real estate</h3>
        <dl>
          <dt>Purchase price</dt><dd>$${realEstate.purchasePrice.toLocaleString()}</dd>
          <dt>Down payment</dt><dd>$${realEstate.downPayment.toLocaleString()} (${realEstate.downPaymentPercent}%)</dd>
          <dt>Loan amount</dt><dd>$${realEstate.loanAmount.toLocaleString()}</dd>
          <dt>Rate / monthly</dt><dd>${realEstate.annualInterestRate}% / $${realEstate.monthlyPayment.toLocaleString()}</dd>
          <dt>Buy date</dt><dd>${realEstate.buyDate}</dd>
          <dt>As-of date</dt><dd>${realEstate.asOfDate}</dd>
          <dt>Remaining balance</dt><dd>$${realEstate.remainingBalance.toLocaleString()}</dd>
          <dt>Est. value at as-of</dt><dd>$${realEstate.estimatedValueAtAsOf.toLocaleString()}</dd>
          <dt>Equity at as-of</dt><dd>$${realEstate.equityAtAsOf.toLocaleString()}</dd>
          <dt>Gain / loss (on down payment)</dt><dd class="${gainClass}">$${realEstate.gainLoss.toLocaleString()} (${realEstate.gainLossPercent >= 0 ? "+" : ""}${realEstate.gainLossPercent.toFixed(2)}%)</dd>
        </dl>
      </div>
    `;
  }
  html += "</div>";
  compareResult.innerHTML = html;
}
