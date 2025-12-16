document.addEventListener("DOMContentLoaded", () => {
  // DOM elements
  const filterToggle = document.getElementById("filterToggle");
  const filterPanel = document.getElementById("filterPanel");
  const categoryFiltersEl = document.getElementById("categoryFilters");
  const tableBody = document.querySelector("tbody");

  // Active categories
  const activeCategories = new Set();
  const categories = [...new Set(PRODUCTS.map(p => p.category))];

  // Create category checkboxes
  categories.forEach(category => {
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = true;
    activeCategories.add(category);

    checkbox.addEventListener("change", () => {
      if (checkbox.checked) {
        activeCategories.add(category);
      } else {
        activeCategories.delete(category);
      }
      render();
    });

    const label = document.createElement("label");
    label.textContent = category;

    categoryFiltersEl.append(checkbox, label, document.createElement("br"));
  });

  // Filter toggle
  filterToggle.addEventListener("click", e => {
    e.preventDefault();
    filterPanel.hidden = !filterPanel.hidden;
  });

  // Render products
  function render() {
    tableBody.innerHTML = "";

    PRODUCTS.filter(p => activeCategories.has(p.category))
      .forEach(p => {
        const viewBtn = `<a class="icon-btn" href="${BASE_URLS.view}?search_term=${p.id}" title="View">
          <img src="/static/images/eye.svg" alt="View"></a>`;

        const editBtn = `<a class="icon-btn" href="${BASE_URLS.edit}?article_id=${p.id}" title="Edit">
          <img src="/static/images/edit.svg" alt="Edit"></a>`;

        const deleteBtn = (accessLevel === "Manager") ? `<a class="icon-btn" href="${BASE_URLS.delete}?article_id=${p.id}" title="Delete"
          onclick="return confirm('Are you sure you want to delete product ${p.id}?');">
          <img src="/static/images/delete.svg" alt="Delete"></a>` : "";

        tableBody.innerHTML += `
          <tr>
            <td class="col-name">${p.name}</td>
            <td class="col-id">${p.id}</td>
            <td class="col-cat">${p.category}</td>
            <td class="col-price">${p.price} kr</td>
            <td class="col-discount">${p.discount}%</td>
            <td class="col-amount">${p.amount} pcs</td>
            <td class="col-actions">${viewBtn}${editBtn}${deleteBtn}</td>
          </tr>`;
      });
  }

  // Initial render
  render();
});
