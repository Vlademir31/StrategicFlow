async function carregarInventory() {
    const resposta = await fetch("/api/v1/inventory", {
        headers: { "X-Tenant-ID": "default-tenant" }
    });

    const itens = await resposta.json();
    const tabela = document.getElementById("tabela-inventory");
    tabela.innerHTML = "";

    itens.forEach(item => {
        tabela.innerHTML += `
            <tr>
                <td>${item.sku}</td>
                <td>${item.sku_name ?? ""}</td>
                <td>${item.quantity_available}</td>
                <td>${item.quantity_reserved}</td>
                <td>${item.location ?? ""}</td>
                <td>${item.class_}</td>
            </tr>
        `;
    });
}
