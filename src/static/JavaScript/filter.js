document.addEventListener("DOMContentLoaded", () => {
  // Filter toggle variables
  const filterToggle = document.getElementById("filterToggle");
  const filterPanel = document.getElementById("filterPanel");
  const categoryFiltersEl = document.getElementById("categoryFilters");
  const priceFiltersEl = document.getElementById("priceFilters");
  const stockFiltersEl = document.getElementById("stockFilters");
  const discountFiltersEl = document.getElementById("discountFilters");
  const tableBody = document.querySelector("tbody");

  // Categories
  const activeCategories = new Set();
  const categories = [...new Set(PRODUCTS.map(product => product.category))];

  // Price ranges
  const prices = PRODUCTS.map(product => product.price);
  const minPrice = 0;
  const maxPrice = Math.max(...prices);
  const priceStep = 2000;
  const priceRanges = Math.ceil((maxPrice - minPrice) / priceStep);

  const priceCheckboxes = [];
  for (let i = 0; i < priceRanges; i++) {
    let min = minPrice + priceStep * i;
    let max = (i === priceRanges - 1) ? Infinity : minPrice + priceStep * (i + 1) - 1;
    let label = (max === Infinity) ? `${min} kr +` : `${min} - ${max} kr`;
    priceCheckboxes.push({ label, min, max });
  }

  const activePriceCheckboxes = new Set(priceCheckboxes.map(check => check.label));

  // Stock ranges
  const stocks = PRODUCTS.map(product => product.amount);
  const minStock = 0;
  const maxStock = Math.max(...stocks);
  const stockStep = 10;
  const stockRanges = Math.ceil((maxStock - minStock) / stockStep);

  const stockCheckboxes = [];
  for (let i = 0; i < stockRanges; i++) {
    let min = minStock + stockStep * i;
    let max = (i === stockRanges - 1) ? Infinity : minStock + stockStep * (i + 1) - 1;
    let label = (max === Infinity) ? `${min} pcs +` : `${min} - ${max} pcs`;
    
    stockCheckboxes.push({ label, min, max });
  }

  const activeStockCheckboxes = new Set(stockCheckboxes.map(check => check.label));

  // Discount ranges
  const discounts = PRODUCTS.map(product => product.discount);
  const minDiscount = 0;
  const maxDiscount = 100;
  const discountStep = 10;
  const discountRanges = 10;

  const discountCheckboxes = [];
  for (let i = 0; i < discountRanges; i++) {
    let min = minDiscount + discountStep * i;
    let max = (i === discountRanges - 1) ? Infinity : minDiscount + discountStep * (i + 1) -1;
    let label = (max === Infinity) ? `${min} % +` : `${min} - ${max} %`;

    discountCheckboxes.push({ label, min, max });
  }

  const activeDiscountCheckboxes = new Set(discountCheckboxes.map(check => check.label));

  // Category checkboxes
  categories.forEach(category => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = true;
    activeCategories.add(category);

    checkbox.addEventListener("change", () => {
      checkbox.checked ? activeCategories.add(category) : activeCategories.delete(category);
      render();
    });

    const categoryLabel = document.createElement("label");
    categoryLabel.textContent = category;

    categoryFiltersEl.append(checkbox, categoryLabel, document.createElement("br"));
  });

  // Price checkboxes
  priceCheckboxes.forEach(range => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = true;
    checkbox.dataset.label = range.label;

    checkbox.addEventListener("change", () => {
      checkbox.checked ? activePriceCheckboxes.add(range.label) : activePriceCheckboxes.delete(range.label);
      render();
    });

    const priceLabel = document.createElement("label");
    priceLabel.textContent = range.label;

    priceFiltersEl.append(checkbox, priceLabel, document.createElement("br"));
  });

  // Stock checkboxes
  stockCheckboxes.forEach(range => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = true;
    checkbox.dataset.label = range.label;

    checkbox.addEventListener("change", () => {
      checkbox.checked ? activeStockCheckboxes.add(range.label) : activeStockCheckboxes.delete(range.label);
      render();
    });

    const stockLabel = document.createElement("label");
    stockLabel.textContent = range.label;

    stockFiltersEl.append(checkbox, stockLabel, document.createElement("br"));
  });

  // Discount checkboxes
  discountCheckboxes.forEach(range => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = true;
    checkbox.dataset.label = range.label;

    checkbox.addEventListener("change", () => {
      checkbox.checked ? activeDiscountCheckboxes.add(range.label) : activeDiscountCheckboxes.delete(range.label);
      render();
    });

    const discountLabel = document.createElement("label");
    discountLabel.textContent = range.label;

    discountFiltersEl.append(checkbox, discountLabel, document.createElement("br"));
  });

  // Filter toggle
  filterToggle.addEventListener("click", e => {
    e.preventDefault();
    filterPanel.hidden = !filterPanel.hidden;
  });

  // Render function
  function render() {
    tableBody.innerHTML = "";

    PRODUCTS.filter(product => {
      const categoryMatch = activeCategories.has(product.category);
      const priceMatch = priceCheckboxes
        .filter(check => activePriceCheckboxes.has(check.label))
        .some(check => product.price >= check.min && product.price <= check.max);
      const stockMatch = stockCheckboxes.length === 0 || stockCheckboxes
        .filter(check => activeStockCheckboxes.has(check.label))
        .some(check => product.amount >= check.min && product.amount <= check.max);
      const discountMatch = discountCheckboxes.length === 0 || discountCheckboxes
        .filter(check => activeDiscountCheckboxes.has(check.label))
        .some(check => product.discount >= check.min && product.discount <= check.max);

      return categoryMatch && priceMatch && stockMatch && discountMatch;

    }).forEach(product => {
      const viewBtn = `<a class="icon-btn" href="${BASE_URLS.view}?search_term=${product.id}" title="View">
        <img src="/static/images/eye.svg" alt="View"></a>`;
      const editBtn = `<a class="icon-btn" href="${BASE_URLS.edit}?article_id=${product.id}" title="Edit">
        <img src="/static/images/edit.svg" alt="Edit"></a>`;
      const deleteBtn = (accessLevel === "Manager") ? `<a class="icon-btn" href="${BASE_URLS.delete}?article_id=${product.id}" title="Delete"
        onclick="return confirm('Are you sure you want to delete product ${product.id}?');">
        <img src="/static/images/delete.svg" alt="Delete"></a>` : "";

      tableBody.innerHTML += `
        <tr>
          <td class="col-name">${product.name}</td>
          <td class="col-id">${product.id}</td>
          <td class="col-cat">${product.category}</td>
          <td class="col-price">${product.price} kr</td>
          <td class="col-discount">${product.discount}%</td>
          <td class="col-amount">${product.amount} pcs</td>
          <td class="col-actions">${viewBtn}${editBtn}${deleteBtn}</td>
        </tr>`;
    });
  }

  // Initial render
  render();
});
