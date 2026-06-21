let dadosGlobais = [];

async function carregarInventoryConsultivo() {
    const tabela = document.getElementById("tabela-inventory");
    const insightsList = document.getElementById("insights-list");
    const alertsBox = document.getElementById("inventory-alerts");

    tabela.innerHTML = "<tr><td colspan='11'>Carregando análise consultiva...</td></tr>";
    insightsList.innerHTML = "";
    alertsBox.innerHTML = "";

    try {
        const resposta = await fetch("http://localhost/api/v1/inventory/dashboard", {
            headers: { "X-Tenant-ID": "default" }
        });

        if (!resposta.ok) {
            tabela.innerHTML = "<tr><td colspan='11'>Erro ao carregar dados consultivos</td></tr>";
            return;
        }

        const dados = await resposta.json();
        dadosGlobais = dados;
        tabela.innerHTML = "";

        let totalValor = 0;
        let estoqueParado = 0;
        let riscoRuptura = 0;
        let excesso = 0;

        const insights = [];

        // Dados para gráficos
        let classeA = 0, classeB = 0, classeC = 0;
        let aging30 = 0, aging60 = 0, aging90 = 0, aging120 = 0;
        let coberturaBaixa = 0, coberturaMedia = 0, coberturaAlta = 0;

        dados.forEach(item => {
            totalValor += item.stock_value || 0;

            if (item.aging_days >= 90) estoqueParado++;
            if (item.risk_of_stockout) riscoRuptura++;
            if (item.has_excess) excesso++;

            // Tabela
            tabela.innerHTML += `
                <tr>
                    <td>${item.sku}</td>
                    <td>${item.sku_name || "-"}</td>
                    <td>${item.quantity_available}</td>
                    <td>${item.quantity_reserved}</td>
                    <td>${item.location || "-"}</td>
                    <td>${item.class_}</td>
                    <td>${item.aging_days ?? "-"}</td>
                    <td>${item.coverage_days ?? "-"}</td>
                    <td>${item.risk_of_stockout ? "⚠️ Sim" : "Não"}</td>
                    <td>${item.has_excess ? "📦 Excesso" : "-"}</td>
                    <td>R$ ${item.stock_value?.toFixed(2) || "0.00"}</td>
                </tr>
            `;

            // Insights automáticos
            if (item.aging_days >= 120) {
                insights.push(`📦 SKU ${item.sku} está parado há ${item.aging_days} dias.`);
            }
            if (item.risk_of_stockout) {
                insights.push(`⚠️ SKU ${item.sku} está com risco de ruptura.`);
            }
            if (item.has_excess) {
                insights.push(`📦 SKU ${item.sku} está com excesso de estoque.`);
            }
            if (item.coverage_days !== null && item.coverage_days <= 5) {
                insights.push(`⏳ SKU ${item.sku} tem cobertura muito baixa (${item.coverage_days} dias).`);
            }

            // ABC
            if (item.class_ === "A") classeA++;
            else if (item.class_ === "B") classeB++;
            else if (item.class_ === "C") classeC++;

            // Aging buckets
            const aging = item.aging_days ?? 0;
            if (aging <= 30) aging30++;
            else if (aging <= 60) aging60++;
            else if (aging <= 90) aging90++;
            else aging120++;

            // Cobertura buckets
            const cov = item.coverage_days ?? 0;
            if (cov <= 7) coberturaBaixa++;
            else if (cov <= 30) coberturaMedia++;
            else coberturaAlta++;
        });

        // KPIs
        document.getElementById("kpi-total-valor").textContent =
            "R$ " + totalValor.toFixed(2);
        document.getElementById("kpi-estoque-parado").textContent = estoqueParado;
        document.getElementById("kpi-risco-ruptura").textContent = riscoRuptura;
        document.getElementById("kpi-excesso").textContent = excesso;

        // Insights
        insightsList.innerHTML = insights.length
            ? insights.map(i => `<li>${i}</li>`).join("")
            : "<li>Nenhum insight crítico no momento.</li>";

        // Alertas inteligentes
        const alertas = [];
        if (riscoRuptura > 0) {
            alertas.push(`⚠️ Existem ${riscoRuptura} SKUs com risco de ruptura.`);
        }
        if (excesso > 0) {
            alertas.push(`📦 Existem ${excesso} SKUs com excesso de estoque.`);
        }
        if (estoqueParado > 0) {
            alertas.push(`⏳ ${estoqueParado} SKUs estão parados há mais de 90 dias.`);
        }
        alertsBox.innerHTML = alertas.length
            ? alertas.map(a => `<div class="alert">${a}</div>`).join("")
            : "<div class='alert'>✅ Nenhum alerta crítico no momento.</div>";

        // Gráficos
        renderizarGraficos({
            classeA, classeB, classeC,
            aging30, aging60, aging90, aging120,
            coberturaBaixa, coberturaMedia, coberturaAlta
        });

    } catch (erro) {
        tabela.innerHTML = "<tr><td colspan='11'>Falha na conexão com o servidor</td></tr>";
        console.error("Erro ao carregar inventory consultivo:", erro);
    }
}

function renderizarGraficos(dados) {
    const { classeA, classeB, classeC,
            aging30, aging60, aging90, aging120,
            coberturaBaixa, coberturaMedia, coberturaAlta } = dados;

    // Limpa gráficos anteriores
    ["chartABC", "chartAging", "chartCobertura"].forEach(id => {
        const canvas = document.getElementById(id);
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });

    new Chart(document.getElementById("chartABC"), {
        type: "pie",
        data: {
            labels: ["Classe A", "Classe B", "Classe C"],
            datasets: [{
                data: [classeA, classeB, classeC],
                backgroundColor: ["#ff6384", "#36a2eb", "#ffcd56"]
            }]
        },
        options: {
            plugins: {
                title: { display: true, text: "Distribuição ABC" }
            }
        }
    });

    new Chart(document.getElementById("chartAging"), {
        type: "bar",
        data: {
            labels: ["0-30 dias", "31-60", "61-90", "90+"],
            datasets: [{
                label: "Aging (Qtd SKUs)",
                data: [aging30, aging60, aging90, aging120],
                backgroundColor: "#4bc0c0"
            }]
        },
        options: {
            plugins: {
                title: { display: true, text: "Distribuição de Aging" }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    new Chart(document.getElementById("chartCobertura"), {
        type: "bar",
        data: {
            labels: ["Baixa (≤7 dias)", "Média (8-30)", "Alta (>30)"],
            datasets: [{
                label: "Cobertura (Qtd SKUs)",
                data: [coberturaBaixa, coberturaMedia, coberturaAlta],
                backgroundColor: "#9966ff"
            }]
        },
        options: {
            plugins: {
                title: { display: true, text: "Distribuição de Cobertura" }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function exportarInventoryCSV() {
    if (!dadosGlobais || !dadosGlobais.length) {
        alert("Nenhum dado para exportar. Atualize o inventory primeiro.");
        return;
    }

    let csv = "SKU;Nome;Disponível;Reservado;Local;Classe;Aging;Cobertura;RiscoRuptura;Excesso;Valor\n";

    dadosGlobais.forEach(item => {
        csv += `${item.sku};${item.sku_name || ""};${item.quantity_available};${item.quantity_reserved};` +
               `${item.location || ""};${item.class_};${item.aging_days ?? ""};${item.coverage_days ?? ""};` +
               `${item.risk_of_stockout ? "SIM" : "NAO"};${item.has_excess ? "SIM" : "NAO"};${item.stock_value || 0}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "inventory_consultivo.csv";
    a.click();

    URL.revokeObjectURL(url);
}

// Carrega automaticamente ao abrir a página
carregarInventoryConsultivo();
