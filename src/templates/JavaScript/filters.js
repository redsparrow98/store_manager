// Pass url for action buttons
const BASE_URLS = {
    view: "{{ url_for('access_product') }}",
  edit: "{{ url_for('update_product_page')}}",
  delete: "{{ url_for('delete_product_page')}}"
}

// Pass products data to JS
const PRODUCTS = Object.entries({{ products | tojson }}).map(
    ([id, item]) => ({
    id: id,
    name: item.article_name,
    category: item.category,
    price: item.price_SEK || item.price,
    amount: item.stock_amount || item.stock,
    discount: item.discount_percentage || 0
})
);

// Pass access level to JS
const accessLevel = "{{ access_level }}";


  // Filter panel toggle
const filterToggle = document.getElementById("filterToggle");
const filterPanel = document.getElementById("filterPanel");
const categoryFiltersEl = document.getElementById("categoryFilters");
const tableBody = document.querySelector("tbody");
filterToggle.addEventListener("click", (e) => {
    e.preventDefault();
  filterPanel.hidden = !filterPanel.hidden;
});

const activeCategories = new Set();
const categories = [...new Set(PRODUCTS.map(p => p.category))];
categories.forEach(category => {
    const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = true;
  activeCategories.add(category);

  checkbox.addEventListener("change", () => {
    checkbox.checked
    ? activeCategories.add(category)
      : activeCategories.delete(category);
      render();
});

  const label = document.createElement("label");
  label.textContent = category;

  categoryFiltersEl.append(checkbox, label, document.createElement("br"));
});

// Render products based on checked filters
function render() {
    tableBody.innerHTML = "";

PRODUCTS
.filter(p => activeCategories.has(p.category))
  .forEach(p => {

    // Action buttons
    const viewBtn = `
    <a class="icon-btn" href="${BASE_URLS.view}?search_term=${p.id}" title="View">
      <img src="{{ url_for('static', filename='images/eye.svg') }}" alt="View">
        </a>`;
      const editBtn = `
    <a class="icon-btn" href="${BASE_URLS.edit}?article_id=${p.id}" title="Edit">
      <img src="{{ url_for('static', filename='images/edit.svg') }}" alt="Edit">
        </a>`;
      const deleteBtn = (accessLevel === "Manager") ? `
    <a class="icon-btn" href="${BASE_URLS.delete}?article_id=${p.id}" title="Delete"
      onclick="return confirm('Are you sure you want to delete product ${p.id}?');">
        <img src="{{ url_for('static', filename='images/delete.svg') }}" alt="Delete">
        </a>` : "";
    
      // Render the row
    tableBody.innerHTML += `
    <tr>
      <td class="col-name">${p.name}</td>
        <td class="col-id">${p.id}</td>
        <td class="col-cat">${p.category}</td>
        <td class="col-price">${p.price} kr</td>
        <td class="col-discount">${p.discount}%</td>
        <td class="col-amount">${p.amount} pcs</td>
        <td class="col-actions">
        <div class="col-actions">
          ${viewBtn}
            ${editBtn}
            ${deleteBtn}
            </div>
          </td>
        </tr>`;
    });
}
  render();
