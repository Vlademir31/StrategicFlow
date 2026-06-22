let packingDadosGlobais = [];

async function carregarPackingConsultivo() {
    const tabela = document.getElementById("tabela-packing");
    const insightsList = document.getElementById("packing-insights-list");
    const alertsBox = document.getElementById("packing-alerts");

    tabela.innerHTML = "<tr><td colspan='13'>Carregando análise consultiva...</td></tr>";
    insightsList.innerHTML = "";
    alertsBox.innerHTML = "";

    try {
        const resposta = await fetch("http://localhost/api/v1/packing/dashboard", {
            headers: { "X-Tenant-ID": "default" }
        });

        if (!resposta.ok) {
            tabela.innerHTML = "<tr><td colspan='13'>Erro ao carregar dados consultivos</td></tr>";
            return;
        }

        const dados = await resposta.json();
        packingDadosGlobais = dados.raw;
        tabela.innerHTML = "";

        document.getElementById("kpi-pack-avg-time").textContent =
            dados.kpis.avg_time.toFixed(1) + " min";
        document.getElementById("kpi-pack-error-rate").textContent =
            dados.kpis.avg_error.toFixed(2) + "%";
        document.getElementById("kpi-pack-damage-rate").textContent =
            dados.kpis.avg_damage.toFixed(2) + "%";
        document.getElementById("kpi-pack-reworks").textContent =
            dados.kpis.reworks;
        document.getElementById("kpi-pack-sla").textContent =
            dados.kpis.sla_rate.toFixed(1) + "%";

        insightsList.innerHTML = dados.insights.length
            ? dados.insights.map(i => `<li>${i.text}</li>`).join("")
            : "<li>Nenhum insight crítico no momento.</li>";

        alertsBox.innerHTML = dados.alerts.length
            ? dados.alerts.map(a => `
                <div class="alert alert-${a.level}">
                    <strong>${a.title}</strong>
                    <p>${a.message}</p>
                </div>
            `).join("")
            : "<div class='alert'>✅ Nenhum alerta crítico no momento.</div>";

        dados.raw.forEach(item => {
            tabela.innerHTML += `
                <tr>
                    <td>${item.order_id}</td>
                    <td>${item.sku}</td>
                    <td>${item.sku_name || "-"}</td>
                    <td>${item.quantity}</td>
                    <td>${item.packing_type || "-"}</td>
                    <td>${item.operator_name || "-"}</td>
                    <td>${item.station || "-"}</td>
                    <td>${item.packing_time_minutes} min</td>
                    <td>${item.error_rate}%</td>
                    <td>${item.damage_rate}%</td>
                    <td>${item.rework ? "❌" : "✔️"}</td>
                    <td>${item.sla_compliance ? "✔️" : "❌"}</td>
                    <td>${formatarData(item.packed_at)}</td>
                </tr>
            `;
        });

        renderizarGraficosPacking(dados.charts);

    } catch (erro) {
        tabela.innerHTML = "<tr><td colspan='13'>Falha na conexão com o servidor</td></tr>";
        console.error("Erro ao carregar packing consultivo:", erro);
    }
}

function renderizarGraficosPacking(charts) {
    new Chart(document.getElementById("chartPackingTempo"), {
        type: "bar",
        data: {
            labels: charts.tempo_por_station.map(i => i.station),
            datasets: [{
                label: "Tempo Médio (min)",
                data: charts.tempo_por_station.map(i => i.avg_time),
                backgroundColor: "#007bff"
            }]
        }
    });

    new Chart(document.getElementById("chartPackingErros"), {
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

    new Chart(document.getElementById("chartPackingDamage"), {
        type: "bar",
        data: {
            labels: charts.damage_por_tipo.map(i => i.type),
            datasets: [{
                label: "Danos (%)",
                data: charts.damage_por_tipo.map(i => i.avg_damage),
                backgroundColor: "#ffc107"
            }]
        }
    });
}

function exportarPackingCSV() {
    if (!packingDadosGlobais.length) {
        alert("Nenhum dado para exportar.");
        return;
    }

    let csv = "Pedido;SKU;Nome;Qtd;Tipo;Operador;Estação;Tempo;Erro;Danos;Retrabalho;SLA;Data\n";

    packingDadosGlobais.forEach(item => {
        csv += `${item.order_id};${item.sku};${item.sku_name || ""};${item.quantity};${item.packing_type || ""};` +
               `${item.operator_name || ""};${item.station || ""};${item.packing_time_minutes};${item.error_rate};` +
               `${item.damage_rate};${item.rework};${item.sla_compliance};${item.packed_at}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "packing_consultivo.csv";
    a.click();
    URL.revokeObjectURL(url);
}

function formatarData(value) {
    if (!value) return "-";
    const d = new Date(value);
    return d.toLocaleString("pt-BR");
}
