let putawayDadosGlobais = [];

// ===============================
// FUNÇÃO PRINCIPAL
// ===============================
async function carregarPutawayConsultivo() {
    const tabela = document.getElementById("tabela-putaway");
    const insightsList = document.getElementById("putaway-insights-list");
    const alertsBox = document.getElementById("putaway-alerts");

    tabela.innerHTML = "<tr><td colspan='10'>Carregando análise consultiva...</td></tr>";
    insightsList.innerHTML = "";
    alertsBox.innerHTML = "";

    try {
        const resposta = await fetch("http://localhost/api/v1/putaway/dashboard", {
            headers: { "X-Tenant-ID": "default" }
        });

        if (!resposta.ok) {
            tabela.innerHTML = "<tr><td colspan='10'>Erro ao carregar dados consultivos</td></tr>";
            return;
        }

        const dados = await resposta.json();
        putawayDadosGlobais = dados.raw;
        tabela.innerHTML = "";

        // KPIs
        document.getElementById("kpi-put-total-time").textContent =
            dados.kpis.avg_total_time.toFixed(1) + " min";

        document.getElementById("kpi-put-travel-time").textContent =
            dados.kpis.avg_travel_time.toFixed(1) + " min";

        document.getElementById("kpi-put-optimal-rate").textContent =
            dados.kpis.optimal_slot_rate.toFixed(1) + "%";

        document.getElementById("kpi-put-non-optimal").textContent =
            dados.kpis.non_optimal_slots;

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
                    <td>${item.sku}</td>
                    <td>${item.sku_name || "-"}</td>
                    <td>${item.quantity}</td>
                    <td>${item.source_location || "-"}</td>
                    <td>${item.target_location || "-"}</td>
                    <td>${item.class_}</td>
                    <td>${item.operator_name || "-"}</td>
                    <td>${item.total_time_minutes} min</td>
                    <td>${item.is_optimal_slot ? "✔️" : "❌"}</td>
                    <td>${formatarData(item.created_at)}</td>
                </tr>
            `;
        });

        // Gráficos
        renderizarGraficosPutaway(dados.charts);

    } catch (erro) {
        tabela.innerHTML = "<tr><td colspan='10'>Falha na conexão com o servidor</td></tr>";
        console.error("Erro ao carregar putaway consultivo:", erro);
    }
}

// ===============================
// GRÁFICOS
// ===============================
function renderizarGraficosPutaway(charts) {

    // Tempo por SKU
    new Chart(document.getElementById("chartPutawayTempo"), {
        type: "bar",
        data: {
            labels: charts.tempo_por_sku.map(i => i.sku),
            datasets: [{
                label: "Tempo Total (min)",
                data: charts.tempo_por_sku.map(i => i.total_time),
                backgroundColor: "#007bff"
            }]
        }
    });

    // Slotting ideal
    new Chart(document.getElementById("chartPutawaySlotting"), {
        type: "pie",
        data: {
            labels: charts.slotting_ideal.map(i => i.label),
            datasets: [{
                data: charts.slotting_ideal.map(i => i.value),
                backgroundColor: ["#28a745", "#dc3545"]
            }]
        }
    });

    // Produtividade por operador
    new Chart(document.getElementById("chartPutawayOperadores"), {
        type: "bar",
        data: {
            labels: charts.produtividade_operador.map(i => i.operator_name),
            datasets: [{
                label: "Tempo Médio (min)",
                data: charts.produtividade_operador.map(i => i.avg_time),
                backgroundColor: "#ffc107"
            }]
        },
        options: { indexAxis: "y" }
    });
}

// ===============================
// EXPORTAÇÃO CSV
// ===============================
function exportarPutawayCSV() {
    if (!putawayDadosGlobais.length) {
        alert("Nenhum dado para exportar.");
        return;
    }

    let csv = "SKU;Nome;Qtd;Origem;Destino;Classe;Operador;Tempo;SlotIdeal;Data\n";

    putawayDadosGlobais.forEach(item => {
        csv += `${item.sku};${item.sku_name || ""};${item.quantity};${item.source_location || ""};` +
               `${item.target_location || ""};${item.class_};${item.operator_name || ""};` +
               `${item.total_time_minutes};${item.is_optimal_slot};${item.created_at}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "putaway_consultivo.csv";
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
