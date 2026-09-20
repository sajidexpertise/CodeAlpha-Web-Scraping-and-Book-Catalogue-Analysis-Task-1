/* Nexus dashboard · all visuals derive from the currently filtered CSV rows. */
(() => {
  "use strict";
  const payload = window.CATALOGUE || {metadata: {}, records: []};
  const meta = payload.metadata || {};
  const all = (payload.records || []).map(row => ({
    title: String(row.title || ""),
    upc: String(row.upc || ""),
    price: Number(row.price_gbp),
    stock: Number(row.stock),
    category: String(row.category || "Unclassified"),
    rating: row.rating === "" || row.rating == null ? null : Number(row.rating),
    url: String(row.url || ""),
  })).filter(row => row.title && Number.isFinite(row.price) && Number.isFinite(row.stock));
  const $ = id => document.getElementById(id);
  const safe = text => String(text).replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[ch]);
  const gbp = n => "£" + Number(n).toFixed(2);
  const sourceUrl = url => /^https:\/\/books\.toscrape\.com\/catalogue\//.test(url) ? url : "https://books.toscrape.com/";
  const binDefs = [
    {label: "£0–19", min: 0, max: 20},
    {label: "£20–29", min: 20, max: 30},
    {label: "£30–39", min: 30, max: 40},
    {label: "£40–49", min: 40, max: 50},
    {label: "£50+", min: 50, max: Infinity},
  ];
  let current = [], page = 0;
  const perPage = 12;

  const categories = [...new Set(all.map(row => row.category).filter(x => x !== "Unclassified"))]
    .sort((a,b) => a.localeCompare(b));
  categories.forEach(category => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    $("categoryFilter").append(option);
  });
  $("sampleNotice").innerHTML = meta.sample
    ? "<b>● VERIFIED STARTER SAMPLE / 20 RECORDS</b> The package includes 20 checked product pages. Run the Python scraper for the broader catalogue, detailed categories and star classes. Site prices and ratings are synthetic."
    : "<b>● LIVE SCRAPER OUTPUT / " + all.length.toLocaleString() + " RECORDS</b> Collected " +
      safe(meta.collected_utc || "date unavailable") + ". Training-site prices and ratings are synthetic.";
  $("dotLabel").textContent = all.length.toLocaleString() + " DOTS";
  $("qualityTag").textContent = meta.sample ? "STARTER SAMPLE" : "LIVE SCRAPE";
  $("dataNote").textContent = meta.sample
    ? "Provenance: first catalogue page and 20 product detail pages. Category and rating were not verified in this sample. This training site does not provide real sales or demand data."
    : "Provenance: " + (meta.pages_visited ?? "?") + " catalogue pages visited; " +
      (meta.skipped_products ?? 0) + " product details skipped. Collected " +
      (meta.collected_utc || "date unavailable") + ". Check reports/skipped_pages.txt when skipped count is nonzero.";

  function filtered() {
    const search = $("search").value.trim().toLocaleLowerCase();
    const band = $("filter").value;
    const category = $("categoryFilter").value;
    const stock = $("stockFilter").value;
    return all.filter(row =>
      (!search || row.title.toLocaleLowerCase().includes(search) || row.upc.toLocaleLowerCase().includes(search)) &&
      (band === "all" || band === "low" && row.price < 25 ||
       band === "mid" && row.price >= 25 && row.price < 40 ||
       band === "high" && row.price >= 40) &&
      (category === "all" || row.category === category) &&
      (stock === "all" || stock === "available" && row.stock > 0 || stock === "zero" && row.stock === 0));
  }

  function histogram(rows) {
    const bins = binDefs.map(b => ({...b, count: rows.filter(row => row.price >= b.min && row.price < b.max).length}));
    const peak = Math.max(1, ...bins.map(b => b.count));
    $("histogram").innerHTML = bins.map((b,i) =>
      `<div class="hcol" title="${b.count} listings, ${b.label}"><span class="hnum">${b.count}</span><div class="hbar" style="height:${Math.max(5,b.count/peak*170)}px;--i:${i}"></div><span class="hlabel">${b.label}</span></div>`).join("");
  }

  function scatter(rows) {
    const xMax = Math.max(60, Math.ceil(Math.max(0,...rows.map(row => row.price)) / 10) * 10);
    const yMax = Math.max(24, Math.max(0,...rows.map(row => row.stock)) + 2);
    const dots = rows.map((row,i) => {
      const x = 35 + row.price / xMax * 450;
      const y = 190 - row.stock / yMax * 160 + (i%4-1.5)*1.5;
      return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${rows.length > 200 ? 3.3 : 5.4}" class="plot-dot"><title>${safe(row.title)} · ${gbp(row.price)} · ${row.stock} units</title></circle>`;
    }).join("");
    $("scatter").innerHTML = `<svg viewBox="0 0 510 218" role="img" aria-label="Displayed price plotted against available units"><g class="plot-grid"><path d="M35 30H485 M35 70H485 M35 110H485 M35 150H485 M35 190H485 M35 30V190 M185 30V190 M335 30V190 M485 30V190" fill="none"/></g>${dots}<g class="plot-labels"><text x="35" y="209">£0</text><text x="178" y="209">£${Math.round(xMax/3)}</text><text x="328" y="209">£${Math.round(xMax*2/3)}</text><text x="465" y="209">£${xMax}</text></g></svg>`;
  }

  function details(rows) {
    const valid = rows.filter(row => row.category !== "Unclassified");
    if (!valid.length) {
      $("categoryChart").innerHTML = '<div class="empty-chart">Category values were not verified in this sample.<br>Run the scraper to extract product breadcrumbs.</div>';
    } else {
      const counts = new Map();
      valid.forEach(row => counts.set(row.category,(counts.get(row.category) || 0)+1));
      const sorted = [...counts].sort((a,b)=>b[1]-a[1]).slice(0,6);
      const largest = Math.max(1,...sorted.map(x=>x[1]));
      $("categoryChart").innerHTML = sorted.map(([label,count]) =>
        `<div class="category-item"><div class="cat-title"><span>${safe(label)}</span><b>${count}</b></div><div class="track"><div class="fill" style="width:${count/largest*100}%"></div></div></div>`).join("");
    }
    const rated = rows.filter(row => Number.isInteger(row.rating) && row.rating >= 1 && row.rating <= 5);
    if (!rated.length) {
      $("ratingChart").innerHTML = '<div class="empty-chart">No verified rating classes in the starter sample.<br>Live product pages include one-to-five star CSS classes.</div>';
    } else {
      const counts = [1,2,3,4,5].map(n => rated.filter(row => row.rating === n).length);
      const largest = Math.max(1,...counts);
      $("ratingChart").innerHTML = counts.map((count,i) =>
        `<div class="rating-item"><b>${i+1} star${i?"s":""}</b><div class="track"><div class="fill" style="width:${count/largest*100}%"></div></div><span>${count}</span></div>`).join("");
    }
  }

  function leaders(rows) {
    const top = [...rows].sort((a,b)=>b.price-a.price).slice(0,4);
    $("topbooks").innerHTML = top.length ? top.map((row,i) =>
      `<a class="bookrow" href="${safe(sourceUrl(row.url))}" target="_blank" rel="noopener"><span class="bookrank">0${i+1}</span><span class="booktitle">${safe(row.title)}</span><strong>${gbp(row.price)}</strong><span class="bookarrow">↗</span></a>`).join("")
      : '<p class="empty">No titles match these filters.</p>';
  }

  function table(rows) {
    const pages = Math.max(1,Math.ceil(rows.length/perPage));
    page = Math.min(Math.max(0,page),pages-1);
    const start = page*perPage;
    $("catalogueRows").innerHTML = rows.slice(start,start+perPage).map(row =>
      `<tr><td><a href="${safe(sourceUrl(row.url))}" target="_blank" rel="noopener">${safe(row.title)} ↗</a><small>UPC: ${safe(row.upc)}</small></td><td>${safe(row.category)}</td><td>${gbp(row.price)}</td><td><span class="stock-chip">${row.stock} units</span></td><td>${row.rating == null ? "—" : safe(row.rating)+" / 5"}</td></tr>`).join("");
    $("pagination").textContent = rows.length ? `Showing ${start+1}–${Math.min(start+perPage,rows.length)} of ${rows.length}` : "No matching records";
    $("prev").disabled = page === 0;
    $("next").disabled = page >= pages-1;
  }

  function render() {
    current = filtered();
    const n = current.length, prices = current.map(row => row.price);
    $("count").textContent = String(n).padStart(2,"0");
    $("avg").textContent = n ? gbp(prices.reduce((a,b)=>a+b,0)/n) : "—";
    $("stock").textContent = current.reduce((sum,row)=>sum+row.stock,0).toLocaleString();
    $("spread").textContent = n ? gbp(Math.max(...prices)-Math.min(...prices)) : "—";
    $("results").textContent = n.toLocaleString() + " of " + all.length.toLocaleString() + " source-linked records";
    histogram(current); scatter(current); details(current); leaders(current); table(current);
  }

  ["search","filter","categoryFilter","stockFilter"].forEach(id =>
    $(id).addEventListener(id === "search" ? "input" : "change", () => {page = 0;render();}));
  $("reset").addEventListener("click", () => {
    $("search").value = ""; $("filter").value = "all"; $("categoryFilter").value = "all";
    $("stockFilter").value = "all"; page = 0;render();
  });
  $("prev").addEventListener("click",()=>{page--;render();});
  $("next").addEventListener("click",()=>{page++;render();});
  $("export").addEventListener("click", () => {
    const columns = ["title","upc","price_gbp","stock","category","rating","url"];
    const quote = value => '"' + String(value ?? "").replace(/"/g,'""') + '"';
    const csv = "\uFEFF" + columns.join(",") + "\r\n" +
      current.map(row => [row.title,row.upc,row.price,row.stock,
        row.category === "Unclassified" ? "" : row.category,row.rating,row.url].map(quote).join(",")).join("\r\n");
    const href = URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
    const link = document.createElement("a");link.href=href;link.download="CodeAlpha_Catalogue_Filtered.csv";link.click();
    setTimeout(()=>URL.revokeObjectURL(href),1000);
  });
  render();
})();
