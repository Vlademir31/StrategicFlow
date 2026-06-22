let shippingDadosGlobais = [];

async function carregarShippingConsultivo() {
    const tabela = document.getElementById("tabela-shipping");
    const insightsList = document.getElementById("shipping-insights-list");
    const alertsBox = document.getElementById("shipping-alerts");

    tabela.innerHTML = "<tr><td colspan='14'>Carregando análise consultiva...</td></tr>";
    insightsList.innerHTML = "";
    alertsBox.innerHTML = "";

    try {
        const resp = await fetch("http://localhost/api/v1/shipping/dashboard", {
            headers: { "X-Tenant-ID": "default" }
        });

        if (!resp.ok) {
            tabela.innerHTML = "<tr><td colspan='14'>Erro ao carregar dados</td></tr>";
            return;
        }

        const dados = await resp.json();
        shippingDadosGlobais = dados.raw;
        tabela.innerHTML = "";

        document.getElementById("kpi-ship-expedition").textContent =
            dados.kpis.avg_expedition.toFixed(1) + " min";
        document.getElementById("kpi-ship-waiting").textContent =
            dados.kpis.avg_waiting.toFixed(1) + " min";
        document.getElementById("kpi-ship-damage").textContent =
            dados.kpis.avg_damage.toFixed(2) + "%";
        document.getElementById("kpi-ship-reworks").textContent =
            dados.kpis.reworks;
        document.getElementById("kpi-ship-sla").textContent =
            dados.kpis.sla_rate.toFixed(1) + "%";

        insightsList.innerHTML = dados.insights.length
            ? dados.insights.map(i => `<li>${i.text}</li>`).join("")
            : "<li>Nenhum insight crítico.</li>";

        alertsBox.innerHTML = dados.alerts.length
            ? dados.alerts.map(a => `
                <div class="alert alert-${a.level}">
                    <strong>${a.title}</strong>
                    <p>${a.message}</p>
                </div>
            `).join("")
            : "<div class='alert'>Nenhum alerta crítico.</div>";

        dados.raw.forEach(item => {
            tabela.innerHTML += `
                <tr>
                    <td>${item.order_id}</td>
                    <td>${item.sku}</td>
                    <td>${item.sku_name || "-"}</td>
                    <td>${item.quantity}</td>
                    <td>${item.carrier || "-"}</td>
                    <td>${item.tracking_code || "-"}</td>
                    <td>${item.vehicle_type || "-"}</td>
                    <td>${item.driver_name || "-"}</td>
                    <td>${item.expedition_time_minutes} min</td>
                    <td>${item.waiting_time_minutes} min</td>
                    <td>${item.damage_rate}%</td>
                    <td>${item.rework ? "❌" : "✔️"}</td>
                    <td>${item.sla_compliance ? "✔️" : "❌"}</td>
                    <td>${formatarData(item.shipped_at)}</td>
                </tr>
            `;
        });

        renderizarGraficosShipping(dados.charts);

    } catch (e) {
        tabela.innerHTML = "<tr><td colspan='14'>Falha na conexão</td></tr>";
        console.error(e);
    }
}

function renderizarGraficosShipping(charts) {

    new Chart(document.getElementById("chartShippingCarrier"), {
        type: "bar",
        data: {
            labels: charts.tempo_por_transportadora.map(i => i.carrier),
            datasets: [{
                label: "Tempo Médio (min)",
                data: charts.tempo_por_transportadora.map(i => i.avg_time),
                backgroundColor: "#007bff"
            }]
        }
    });

    new Chart(document.getElementById("chartShippingDamage"), {
        type: "bar",
        data: {
            labels: charts.danos_por_sku.map(i => i.sku),
            datasets: [{
                label: "Danos (%)",
                data: charts.danos_por_sku.map(i => i.avg_damage),
                backgroundColor: "#dc3545"
            }]
        }
    });

    new Chart(document.getElementById("chartShippingWait"), {
        type: "line",
        data: {
            labels: charts.espera_por_dia.map(i => i.date),
            datasets: [{
                label: "Espera Média (min)",
                data: charts.espera_por_dia.map(i => i.avg_wait),
                borderColor: "#ffc107",
                backgroundColor: "rgba(255,193,7,0.2)"
            }]
        }
    });
}

function exportarShippingCSV() {
    if (!shippingDadosGlobais.length) {
        alert("Nenhum dado para exportar.");
        return;
    }

    let csv = "Pedido;SKU;Nome;Qtd;Transportadora;Tracking;Veículo;Motorista;Expedição;Espera;Danos;Retrabalho;SLA;Data\n";

    shippingDadosGlobais.forEach(item => {
        csv += `${item.order_id};${item.sku};${item.sku_name || ""};${item.quantity};${item.carrier || ""};` +
               `${item.tracking_code || ""};${item.vehicle_type || ""};${item.driver_name || ""};` +
               `${item.expedition_time_minutes};${item.waiting_time_minutes};${item.damage_rate};` +
               `${item.rework};${item.sla_compliance};${item.shipped_at}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "shipping_consultivo.csv";
    a.click();
    URL.revokeObjectURL(url);
}

function formatarData(v) {
    if (!v) return "-";
    return new Date(v).toLocaleString("pt-BR");
}
