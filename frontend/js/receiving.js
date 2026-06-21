let receivingDadosGlobais = [];

// ===============================
// FUNÇÃO PRINCIPAL
// ===============================
async function carregarReceivingConsultivo() {
    const tabela = document.getElementById("tabela-receiving");
    const insightsList = document.getElementById("receiving-insights-list");
    const alertsBox = document.getElementById("receiving-alerts");

    tabela.innerHTML = "<tr><td colspan='10'>Carregando análise consultiva...</td></tr>";
    insightsList.innerHTML = "";
    alertsBox.innerHTML = "";

    try {
        const resposta = await fetch("http://localhost/api/v1/receiving/dashboard", {
            headers: { "X-Tenant-ID": "default" }
        });

        if (!resposta.ok) {
            tabela.innerHTML = "<tr><td colspan='10'>Erro ao carregar dados consultivos</td></tr>";
            return;
        }

        const dados = await resposta.json();
        receivingDadosGlobais = dados;
        tabela.innerHTML = "";

        // KPIs
        let tempoMedio = 0;
        let divergenciaMedia = 0;
        let produtividadeMedia = 0;
        let gargalos = 0;
        let sla = 0;

        // Insights
        const insights = [];

        // Dados para gráficos
        let tempoPorDia = {};
        let divergenciaPorSKU = {};
        let produtividadePorOperador = {};
        let volumePorDoca = {};

        dados.forEach(item => {
            // KPIs
            tempoMedio += item.cycle_time_minutes || 0;
            divergenciaMedia += item.divergence_rate || 0;
            produtividadeMedia += item.units_per_hour || 0;
            if (item.is_bottleneck) gargalos++;
            if (item.sla_compliance) sla++;

            // Tabela
            tabela.innerHTML += `
                <tr>
                    <td>${item.nf_number}</td>
                    <td>${item.sku}</td>
                    <td>${item.quantity_expected}</td>
                    <td>${item.quantity_received}</td>
                    <td>${(item.divergence_rate || 0).toFixed(2)}%</td>
                    <td>${item.operator_name || "-"}</td>
                    <td>${item.dock_number || "-"}</td>
                    <td>${(item.cycle_time_minutes || 0)} min</td>
                    <td>${item.sla_compliance ? "✔️" : "❌"}</td>
                    <td>${formatarData(item.created_at)}</td>
                </tr>
            `;

            // Insights automáticos
            if (item.waiting_time_minutes >= 60)
                insights.push(`⏳ NF ${item.nf_number} ficou parada ${item.waiting_time_minutes} min na doca.`);

            if (item.divergence_rate > 5)
                insights.push(`⚠️ SKU ${item.sku} teve divergência de ${item.divergence_rate.toFixed(2)}%.`);

            if (item.units_per_hour < 20)
                insights.push(`📉 Operador ${item.operator_name} está com baixa produtividade (${item.units_per_hour} u/h).`);

            if (!item.sla_compliance)
                insights.push(`🚨 NF ${item.nf_number} violou o SLA de recebimento.`);

            // Gráficos – Tempo por dia
            const dia = item.created_at.split("T")[0];
            tempoPorDia[dia] = tempoPorDia[dia] || [];
            tempoPorDia[dia].push(item.cycle_time_minutes || 0);

            // Gráficos – Divergência por SKU
            divergenciaPorSKU[item.sku] = divergenciaPorSKU[item.sku] || [];
            divergenciaPorSKU[item.sku].push(item.divergence_rate || 0);

            // Gráficos – Produtividade por operador
            produtividadePorOperador[item.operator_name] =
                produtividadePorOperador[item.operator_name] || [];
            produtividadePorOperador[item.operator_name].push(item.units_per_hour || 0);

            // Gráficos – Volume por doca
            volumePorDoca[item.dock_number] = (volumePorDoca[item.dock_number] || 0) + item.quantity_received;
        });

        // KPIs finais
        document.getElementById("kpi-rec-tempo-medio").textContent =
            (tempoMedio / dados.length).toFixed(1) + " min";

        document.getElementById("kpi-rec-divergencia").textContent =
            (divergenciaMedia / dados.length).toFixed(2) + "%";

        document.getElementById("kpi-rec-produtividade").textContent =
            (produtividadeMedia / dados.length).toFixed(1) + " u/h";

        document.getElementById("kpi-rec-gargalos").textContent = gargalos;

        document.getElementById("kpi-rec-sla").textContent =
            ((sla / dados.length) * 100).toFixed(1) + "%";

        // Insights
        insightsList.innerHTML = insights.length
            ? insights.map(i => `<li>${i}</li>`).join("")
            : "<li>Nenhum insight crítico no momento.</li>";

        // Alertas inteligentes
        const alertas = [];
        if (gargalos > 0) alertas.push(`🚨 Existem ${gargalos} docas com gargalo.`);
        if (divergenciaMedia / dados.length > 5) alertas.push(`⚠️ Divergência média acima de 5%.`);
        if ((sla / dados.length) < 90) alertas.push(`❌ SLA abaixo de 90%.`);

        alertsBox.innerHTML = alertas.length
            ? alertas.map(a => `<div class="alert">${a}</div>`).join("")
            : "<div class='alert'>✅ Nenhum alerta crítico no momento.</div>";

        // Gráficos
        renderizarGraficosReceiving({
            tempoPorDia,
            divergenciaPorSKU,
            produtividadePorOperador,
            volumePorDoca
        });

    } catch (erro) {
        tabela.innerHTML = "<tr><td colspan='10'>Falha na conexão com o servidor</td></tr>";
        console.error("Erro ao carregar receiving consultivo:", erro);
    }
}

// ===============================
// GRÁFICOS
// ===============================
function renderizarGraficosReceiving(dados) {
    const { tempoPorDia, divergenciaPorSKU, produtividadePorOperador, volumePorDoca } = dados;

    // Tempo médio por dia
    new Chart(document.getElementById("chartReceivingTempo"), {
        type: "line",
        data: {
            labels: Object.keys(tempoPorDia),
            datasets: [{
                label: "Tempo médio (min)",
                data: Object.values(tempoPorDia).map(arr => arr.reduce((a,b)=>a+b,0)/arr.length),
                borderColor: "#007bff",
                backgroundColor: "rgba(0,123,255,0.2)"
            }]
        }
    });

    // Divergência por SKU
    new Chart(document.getElementById("chartReceivingDivergencia"), {
        type: "bar",
        data: {
            labels: Object.keys(divergenciaPorSKU),
            datasets: [{
                label: "Divergência (%)",
                data: Object.values(divergenciaPorSKU).map(arr => arr.reduce((a,b)=>a+b,0)/arr.length),
                backgroundColor: "rgba(220,53,69,0.6)"
            }]
        }
    });

    // Produtividade por operador
    new Chart(document.getElementById("chartReceivingOperadores"), {
        type: "bar",
        data: {
            labels: Object.keys(produtividadePorOperador),
            datasets: [{
                label: "Produtividade (u/h)",
                data: Object.values(produtividadePorOperador).map(arr => arr.reduce((a,b)=>a+b,0)/arr.length),
                backgroundColor: "rgba(40,167,69,0.6)"
            }]
        },
        options: { indexAxis: "y" }
    });

    // Volume por doca
    new Chart(document.getElementById("chartReceivingDocas"), {
        type: "bar",
        data: {
            labels: Object.keys(volumePorDoca),
            datasets: [{
                label: "Volume (unidades)",
                data: Object.values(volumePorDoca),
                backgroundColor: "rgba(255,193,7,0.6)"
            }]
        }
    });
}

// ===============================
// EXPORTAÇÃO CSV
// ===============================
function exportarReceivingCSV() {
    if (!receivingDadosGlobais.length) {
        alert("Nenhum dado para exportar.");
        return;
    }

    let csv = "NF;SKU;Esperado;Recebido;Divergencia;Operador;Doca;Tempo;SLA;Data\n";

    receivingDadosGlobais.forEach(item => {
        csv += `${item.nf_number};${item.sku};${item.quantity_expected};${item.quantity_received};` +
               `${item.divergence_rate};${item.operator_name};${item.dock_number};` +
               `${item.cycle_time_minutes};${item.sla_compliance};${item.created_at}\n`;
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "receiving_consultivo.csv";
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
