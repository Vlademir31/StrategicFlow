let pickingDadosGlobais = [];

// ===============================
// FUNÇÃO PRINCIPAL
// ===============================
async function carregarPickingConsultivo() {
    const tabela = document.getElementById("tabela-picking");
    const insightsList = document.getElementById("picking-insights-list");
    const alertsBox = document.getElementById("picking-alerts");

    tabela.innerHTML = "<tr><td colspan='12'>Carregando análise consultiva...</td></tr>";
    insightsList.innerHTML = "";
    alertsBox.innerHTML = "";

    try {
        const resposta = await fetch("http://localhost/api/v1/picking/dashboard", {
            headers: { "X-Tenant-ID": "default" }
        });

        if (!resposta.ok) {
            tabela.innerHTML = "<tr><td colspan='12'>Erro ao carregar dados consultivos</td></tr>";
            return;
        }

        const dados = await resposta.json();
        pickingDadosGlobais = dados.raw;
        tabela.innerHTML = "";

        // KPIs
        document.getElementById("kpi-pick-avg-time").textContent =
            dados.kpis.avg_time.toFixed(1) + " min";

        document.getElementById("kpi-pick-error-rate").textContent =
            dados.kpis.avg_error.toFixed(2) + "%";

        document.getElementById("kpi-pick-productivity").textContent =
            dados.kpis.avg_productivity.toFixed(1) + " u/h";

        document.getElementById("kpi-pick-divergences").textContent =
            dados.kpis.divergences;

        document.getElementById("kpi-pick-sla").textContent =
            dados.kpis.sla_rate.toFixed(1) + "%";

        // Insights
        insightsList.innerHTML = dados.insights.length
            ? dados.insights.map(i => `<li>${i.text}</li>`).join("")
            : "<li>Nenhum insight crítico no momento.</li>";

        // Alertas
        alertsBox.innerHTML = dados.alerts.length
            ? dados.alerts.map(a => `
                <div class="alert alert-${a.level}">
                    <strong>${a.title}</strong>
                    <p>${a.message}</p>
                </div>
            `).join("")
            : "<div class='alert'>✅ Nenhum alerta crítico no momento.</div>";

        // Tabela
        dados.raw.forEach(item => {
            tabela.innerHTML += `
                <tr>
                    <td>${item.order_id}</td>
                    <td>${item.sku}</td>
                    <td>${item.sku_name || "-"}</td>
                    <td>${item.quantity}</td>
                    <td>${item.zone || "-"}</td>
                    <td>${item.operator_name || "-"}</td>
                    <td>${item.picking_time_minutes} min</td>
                    <td>${item.productivity_units_per_hour} u/h</td>
                    <td>${item.error_rate}%</td>
                    <td>${item.divergence ? "❌" : "✔️"}</td>
                    <td>${item.sla_compliance ? "✔️" : "❌"}</td>
                    <td>${formatarData(item.picked_at)}</td>
                </tr>
            `;
        });

        // Gráficos
        renderizarGraficosPicking(dados.charts);

    } catch (erro) {
        tabela.innerHTML = "<tr><td colspan='12'>Falha na conexão com o servidor</td></tr>";
        console.error("Erro ao carregar picking consultivo:", erro);
    }
}

// ===============================
// GRÁFICOS
// ===============================
function renderizarGraficosPicking(charts) {

    // Produtividade por operador
    new Chart(document.getElementById("chartPickingProd"), {
        type: "bar",
        data: {
            labels: charts.prod_por_operador.map(i => i.operator),
            datasets: [{
                label: "Produtividade (u/h)",
                data: charts.prod_por_operador.map(i => i.avg_prod),
                backgroundColor: "#28a745"
            }]
        },
        options: { indexAxis: "y" }
    });

    // Erros por SKU
    new Chart(document.getElementById("chartPickingErros"), {
        type: "bar",
        data: {
            labels: charts.erros_por_sku.map(i => i.sku),
            datasets: [{
                label: "Erro (%)",
                data: charts.erros_por_sku.map(i => i.avg_error),
                backgroundColor: "#dc3545"
            }]
        }
    });

    // Tempo médio por dia
    new Chart(document.getElementById("chartPickingTempo"), {
        type: "line",
        data: {
            labels: charts.tempo_por_dia.map(i => i.date),
            datasets: [{
                label: "Tempo Médio (min)",
                data: charts.tempo_por_dia.map(i => i.avg_time),
                borderColor: "#007bff",
                backgroundColor: "rgba(0,123,255,0.2)"
            }]
        }
    });
}

// ===============================
// EXPORTAÇÃO CSV
// ===============================
function exportarPickingCSV() {
    if (!pickingDadosGlobais.length) {
        alert("Nenhum dado para exportar.");
        return;
    }

    let csv = "Pedido;SKU;Nome;Qtd;Zona;Operador;Tempo;Produtividade;Erro;Divergência;SLA;Data\n";

    pickingDadosGlobais.forEach(item => {
        csv += `${item.order_id};${item.sku};${item.sku_name || ""};${item.quantity};${item.zone || ""};` +
               `${item.operator_name || ""};${item.picking_time_minutes};${item.productivity_units_per_hour};` +
               `${item.error_rate};${item.divergence};${item.sla_compliance};${item.picked_at}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "picking_consultivo.csv";
    a.click();

    URL.revokeObjectURL(url);
}

// ===============================
// UTILITÁRIOS
// ===============================
function formatarData(value) {
    if (!value) return "-";
    const d = new Date(value);
    return d.toLocaleString("pt-BR");
}
