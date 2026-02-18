const compareBtn = document.getElementById("compare-btn");
const compareResult = document.getElementById("compare-result");
const compareError = document.getElementById("compare-error");

// Store address lookups so user can pick one for purchase price
let savedLookups = [];

function addLookupToDropdown(formattedAddress, price) {
  savedLookups.push({ address: formattedAddress, price });
  const sel = document.getElementById("purchasePriceLookup");
  while (sel.options.length > 1) sel.remove(1);
  savedLookups.forEach((lu, i) => {
    const opt = document.createElement("option");
    opt.value = String(lu.price);
    opt.textContent = `${lu.address} — $${Number(lu.price).toLocaleString()}`;
    sel.appendChild(opt);
  });
}

document.getElementById("purchasePriceLookup").addEventListener("change", function () {
  const val = this.value;
  const purchaseInput = document.getElementById("purchasePrice");
  if (val) purchaseInput.value = val;
});

// Property value by address with local state/city helpers
const addressForm = document.getElementById("address-form");
const addressBtn = document.getElementById("address-btn");
const addressResult = document.getElementById("address-result");
const addressError = document.getElementById("address-error");
const addrStreetEl = document.getElementById("addrStreet");
const addrCityEl = document.getElementById("addrCity");
const addrStateEl = document.getElementById("addrState");
const addrZipEl = document.getElementById("addrZip");
const citySuggestionsEl = document.getElementById("city-suggestions");

const US_STATES = [
  ["AL", "Alabama"],
  ["AZ", "Arizona"],
  ["CA", "California"],
  ["CO", "Colorado"],
  ["FL", "Florida"],
  ["GA", "Georgia"],
  ["IL", "Illinois"],
  ["MA", "Massachusetts"],
  ["NC", "North Carolina"],
  ["NY", "New York"],
  ["OH", "Ohio"],
  ["PA", "Pennsylvania"],
  ["TX", "Texas"],
  ["WA", "Washington"],
];

US_STATES.forEach(([code, name]) => {
  const opt = document.createElement("option");
  opt.value = code;
  opt.textContent = `${code} – ${name}`;
  addrStateEl.appendChild(opt);
});

let usCitiesByState = null;
let citiesLoaded = false;

async function ensureCitiesLoaded() {
  if (citiesLoaded) return;
  try {
    const res = await fetch("us-cities.json");
    if (!res.ok) return;
    usCitiesByState = await res.json();
    citiesLoaded = true;
  } catch {
    // ignore; suggestions will just not show
  }
}

function hideCitySuggestions() {
  citySuggestionsEl.style.display = "none";
  citySuggestionsEl.innerHTML = "";
}

async function updateCitySuggestions() {
  const state = addrStateEl.value;
  const query = addrCityEl.value.trim().toLowerCase();
  if (!state || query.length < 2) {
    hideCitySuggestions();
    return;
  }
  await ensureCitiesLoaded();
  if (!usCitiesByState || !usCitiesByState[state]) {
    hideCitySuggestions();
    return;
  }
  const all = usCitiesByState[state];
  const matches = all.filter((c) => c.toLowerCase().startsWith(query)).slice(0, 8);
  if (matches.length === 0) {
    hideCitySuggestions();
    return;
  }
  citySuggestionsEl.innerHTML = "";
  matches.forEach((city) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = city;
    btn.addEventListener("click", () => {
      addrCityEl.value = city;
      hideCitySuggestions();
      addrCityEl.focus();
    });
    citySuggestionsEl.appendChild(btn);
  });
  citySuggestionsEl.style.display = "block";
}

addrCityEl.addEventListener("input", () => {
  updateCitySuggestions();
});
addrStateEl.addEventListener("change", () => {
  updateCitySuggestions();
});
document.addEventListener("click", (e) => {
  if (!citySuggestionsEl.contains(e.target) && e.target !== addrCityEl) {
    hideCitySuggestions();
  }
});

addressForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  addressError.textContent = "";
  addressResult.innerHTML = "";

  const street = addrStreetEl.value.trim();
  const city = addrCityEl.value.trim();
  const state = addrStateEl.value;
  const zip = addrZipEl.value.trim();
  if (!street || !city || !state || !zip) {
    addressError.textContent = "Enter street, city, state, and ZIP.";
    return;
  }
  const address = `${street}, ${city}, ${state}, ${zip}`;

  addressBtn.disabled = true;
  try {
    const res = await fetch(`/api/real-estate/value?${new URLSearchParams({ address })}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");
    const addr = data.formattedAddress || data.address || address;
    const price = data.price != null ? Number(data.price) : null;
    if (addr && price != null) addLookupToDropdown(addr, price);
    addressResult.innerHTML = `
      <dl>
        <dt>Address</dt><dd>${addr}</dd>
        <dt>Est. value</dt><dd>$${price.toLocaleString()}</dd>
        ${data.priceRangeLow != null && data.priceRangeHigh != null ? `<dt>Range</dt><dd>$${Number(data.priceRangeLow).toLocaleString()} – $${Number(data.priceRangeHigh).toLocaleString()}</dd>` : ""}
      </dl>
    `;
  } catch (err) {
    addressError.textContent = err.message;
  } finally {
    addressBtn.disabled = false;
  }
});

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
    const [compareRes, tsRes] = await Promise.all([
      fetch(`/api/compare?${params}`),
      fetch(`/api/compare/time-series?${params}`),
    ]);
    const data = await compareRes.json();
    if (!compareRes.ok) {
      throw new Error(data.error || "Request failed");
    }
    renderCompareResult(data);
    const tsData = tsRes.ok ? await tsRes.json() : null;
    renderCompareChart(tsData);
  } catch (err) {
    compareError.textContent = err.message;
    renderCompareChart(null);
  } finally {
    compareBtn.disabled = false;
  }
});

let compareChartInstance = null;

function renderCompareChart(tsData) {
  const container = document.getElementById("chart-container");
  const canvas = document.getElementById("compare-chart");
  if (!tsData || (!tsData.stock && !tsData.realEstate) || !tsData.years || tsData.years.length === 0) {
    container.style.display = "none";
    if (compareChartInstance) {
      compareChartInstance.destroy();
      compareChartInstance = null;
    }
    return;
  }
  container.style.display = "block";
  if (compareChartInstance) compareChartInstance.destroy();

  const datasets = [];
  if (tsData.stock && tsData.stock.values && tsData.stock.values.some(v => v != null)) {
    datasets.push({
      label: "Stocks (value)",
      data: tsData.stock.values,
      borderColor: "rgb(88, 166, 255)",
      backgroundColor: "rgba(88, 166, 255, 0.1)",
      fill: false,
      tension: 0.2,
      spanGaps: false,
    });
  }
  if (tsData.realEstate && tsData.realEstate.values && tsData.realEstate.values.some(v => v != null)) {
    datasets.push({
      label: "Real estate (equity)",
      data: tsData.realEstate.values,
      borderColor: "rgb(63, 185, 80)",
      backgroundColor: "rgba(63, 185, 80, 0.1)",
      fill: false,
      tension: 0.2,
      spanGaps: false,
    });
  }
  if (datasets.length === 0) {
    container.style.display = "none";
    return;
  }

  compareChartInstance = new Chart(canvas, {
    type: "line",
    data: {
      labels: tsData.years,
      datasets,
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: {
        legend: { position: "top" },
        tooltip: {
          callbacks: {
            label: (ctx) => ctx.dataset.label + ": $" + (ctx.raw != null ? Number(ctx.raw).toLocaleString() : "—"),
          },
        },
      },
      scales: {
        x: { title: { display: true, text: "Year" } },
        y: {
          title: { display: true, text: "Value ($)" },
          ticks: { callback: (v) => "$" + Number(v).toLocaleString() },
        },
      },
    },
  });
}

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
