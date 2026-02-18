/* ═══════════════════════════════════════════
   YW Finance Lab — Chart Engine
   Chart.js 4.x wrapper with dark theme
   ═══════════════════════════════════════════ */

// ─── Global Defaults ───
function initChartDefaults() {
    if (typeof Chart === 'undefined') return;

    Chart.defaults.color = '#9ca3af';
    Chart.defaults.borderColor = '#1f1f2e';
    Chart.defaults.font.family = "'JetBrains Mono', monospace";
    Chart.defaults.font.size = 11;
    Chart.defaults.plugins.legend.display = false;
    Chart.defaults.plugins.tooltip.backgroundColor = '#16161f';
    Chart.defaults.plugins.tooltip.borderColor = '#2a2a3a';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.titleFont = { family: "'JetBrains Mono', monospace", size: 11 };
    Chart.defaults.plugins.tooltip.bodyFont = { family: "'JetBrains Mono', monospace", size: 11 };
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.animation.duration = 600;
}

// ─── Chart Instances Registry ───
const chartInstances = {};

function destroyChart(canvasId) {
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
        delete chartInstances[canvasId];
    }
}

// ─── Time Series Line Chart ───
function createTimeSeries(canvasId, config) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');

    const { labels, data, label, color, fill, yUnit } = config;
    const lineColor = color || '#d4a853';

    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, lineColor + '33');
    gradient.addColorStop(1, lineColor + '00');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: label || '',
                data,
                borderColor: lineColor,
                borderWidth: 2,
                backgroundColor: fill !== false ? gradient : 'transparent',
                fill: fill !== false,
                tension: 0.3,
                pointRadius: 0,
                pointHitRadius: 10,
                pointHoverRadius: 4,
                pointHoverBackgroundColor: lineColor,
                pointHoverBorderColor: '#0a0a0f',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        maxTicksLimit: 8,
                        maxRotation: 0,
                        font: { size: 10 }
                    }
                },
                y: {
                    grid: { color: '#1f1f2e' },
                    ticks: {
                        callback: function(val) {
                            if (yUnit === '%') return val.toFixed(1) + '%';
                            if (yUnit === '$') return '$' + val.toLocaleString();
                            if (yUnit === '원') return val.toLocaleString() + '원';
                            return val.toLocaleString();
                        },
                        font: { size: 10 }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            let val = ctx.parsed.y;
                            if (yUnit === '%') return val.toFixed(2) + '%';
                            if (yUnit === '$') return '$' + val.toLocaleString();
                            if (yUnit === '원') return val.toLocaleString() + '원';
                            return val.toLocaleString();
                        }
                    }
                }
            }
        }
    });

    chartInstances[canvasId] = chart;
    return chart;
}

// ─── Sparkline (mini chart for panels) ───
function createSparkline(canvasId, data, color) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    const lineColor = color || '#d4a853';

    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, lineColor + '44');
    gradient.addColorStop(1, lineColor + '00');

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map((_, i) => i),
            datasets: [{
                data,
                borderColor: lineColor,
                borderWidth: 1.5,
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { x: { display: false }, y: { display: false } },
            plugins: { tooltip: { enabled: false }, legend: { display: false } },
            animation: { duration: 400 }
        }
    });

    chartInstances[canvasId] = chart;
    return chart;
}

// ─── Gauge Chart (Fear & Greed) ───
function createGauge(canvasId, value) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');

    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [
                    getGaugeColor(value),
                    '#1f1f2e'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            circumference: 180,
            rotation: -90,
            cutout: '75%',
            plugins: {
                tooltip: { enabled: false },
                legend: { display: false }
            },
            animation: {
                animateRotate: true,
                duration: 800
            }
        }
    });

    chartInstances[canvasId] = chart;
    return chart;
}

function getGaugeColor(value) {
    if (value <= 20) return '#ef4444';
    if (value <= 40) return '#f97316';
    if (value <= 60) return '#d4a853';
    if (value <= 80) return '#84cc16';
    return '#22c55e';
}

function getGaugeLabel(value) {
    if (value <= 20) return { text: t('extremeFear'), cls: 'extreme-fear' };
    if (value <= 40) return { text: t('fear'), cls: 'fear' };
    if (value <= 60) return { text: t('neutral'), cls: 'neutral' };
    if (value <= 80) return { text: t('greed'), cls: 'greed' };
    return { text: t('extremeGreed'), cls: 'extreme-greed' };
}

// ─── Multi-Series Chart (Comparison) ───
function createMultiSeries(canvasId, seriesArray) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');

    const colors = ['#d4a853', '#3b82f6', '#22c55e', '#ef4444', '#a78bfa', '#22d3ee'];
    const datasets = seriesArray.map((s, i) => ({
        label: s.label,
        data: s.data,
        borderColor: colors[i % colors.length],
        borderWidth: 2,
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.3,
        pointRadius: 0,
        pointHitRadius: 8,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: colors[i % colors.length],
        yAxisID: i === 0 ? 'y' : 'y1'
    }));

    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: seriesArray[0]?.labels || [],
            datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#9ca3af',
                        font: { family: "'JetBrains Mono', monospace", size: 10 },
                        boxWidth: 12,
                        padding: 12
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { maxTicksLimit: 8, maxRotation: 0, font: { size: 10 } }
                },
                y: {
                    position: 'left',
                    grid: { color: '#1f1f2e' },
                    ticks: {
                        font: { size: 10 },
                        color: colors[0]
                    }
                },
                y1: {
                    position: 'right',
                    grid: { display: false },
                    ticks: {
                        font: { size: 10 },
                        color: seriesArray.length > 1 ? colors[1] : '#9ca3af'
                    }
                }
            }
        }
    });

    chartInstances[canvasId] = chart;
    return chart;
}

// ─── Bar Chart ───
function createBar(canvasId, config) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');

    const { labels, data, colors, label } = config;

    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: label || '',
                data,
                backgroundColor: colors || data.map(() => '#d4a85366'),
                borderColor: colors || data.map(() => '#d4a853'),
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 } }
                },
                y: {
                    grid: { color: '#1f1f2e' },
                    ticks: { font: { size: 10 } }
                }
            }
        }
    });

    chartInstances[canvasId] = chart;
    return chart;
}
