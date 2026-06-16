const weeklyCompletionData = document.getElementById("weekly-completion-data");
const progressFill = document.querySelector(".progress-fill");
let weeklyCompletion = {
  labels: [],
  values: [],
};

if (weeklyCompletionData) {
  weeklyCompletion = JSON.parse(weeklyCompletionData.textContent);
}

if (progressFill) {
  const progress = Number(progressFill.dataset.progress || 0);
  progressFill.style.width = `${Math.min(Math.max(progress, 0), 100)}%`;
}

const chartCanvas = document.getElementById("weeklyCompletionChart");

function drawFallbackLineChart(canvas, data) {
  const parent = canvas.parentElement;
  const width = parent.clientWidth;
  const height = parent.clientHeight;
  const scale = window.devicePixelRatio || 1;
  const padding = {
    top: 24,
    right: 20,
    bottom: 38,
    left: 44,
  };
  const values = data.values.length ? data.values : [0];
  const labels = data.labels.length ? data.labels : [""];
  const context = canvas.getContext("2d");

  canvas.width = width * scale;
  canvas.height = height * scale;
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  context.scale(scale, scale);
  context.clearRect(0, 0, width, height);

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const yForValue = (value) => padding.top + chartHeight - (value / 100) * chartHeight;
  const xForIndex = (index) => {
    if (labels.length === 1) {
      return padding.left + chartWidth / 2;
    }

    return padding.left + (index / (labels.length - 1)) * chartWidth;
  };

  context.strokeStyle = "#efedf6";
  context.lineWidth = 1;
  context.font = "700 12px system-ui, sans-serif";
  context.fillStyle = "#6f6a7c";

  [0, 25, 50, 75, 100].forEach((tick) => {
    const y = yForValue(tick);
    context.beginPath();
    context.moveTo(padding.left, y);
    context.lineTo(width - padding.right, y);
    context.stroke();
    context.fillText(`${tick}%`, 4, y + 4);
  });

  labels.forEach((label, index) => {
    context.fillText(label, xForIndex(index) - 12, height - 10);
  });

  const area = new Path2D();
  const line = new Path2D();

  values.forEach((value, index) => {
    const x = xForIndex(index);
    const y = yForValue(value);

    if (index === 0) {
      line.moveTo(x, y);
      area.moveTo(x, y);
      return;
    }

    line.lineTo(x, y);
    area.lineTo(x, y);
  });

  area.lineTo(xForIndex(values.length - 1), padding.top + chartHeight);
  area.lineTo(xForIndex(0), padding.top + chartHeight);
  area.closePath();

  const gradient = context.createLinearGradient(0, padding.top, 0, height);
  gradient.addColorStop(0, "rgba(109, 74, 255, 0.24)");
  gradient.addColorStop(1, "rgba(109, 74, 255, 0)");
  context.fillStyle = gradient;
  context.fill(area);

  context.strokeStyle = "#6d4aff";
  context.lineWidth = 4;
  context.lineCap = "round";
  context.lineJoin = "round";
  context.stroke(line);

  values.forEach((value, index) => {
    const x = xForIndex(index);
    const y = yForValue(value);
    context.beginPath();
    context.arc(x, y, 5, 0, Math.PI * 2);
    context.fillStyle = "#ffffff";
    context.fill();
    context.lineWidth = 3;
    context.strokeStyle = "#6d4aff";
    context.stroke();
  });
}

if (chartCanvas && window.Chart) {
  const context = chartCanvas.getContext("2d");
  const gradient = context.createLinearGradient(0, 0, 0, 320);
  gradient.addColorStop(0, "rgba(109, 74, 255, 0.26)");
  gradient.addColorStop(1, "rgba(109, 74, 255, 0)");

  new Chart(chartCanvas, {
    type: "line",
    data: {
      labels: weeklyCompletion.labels,
      datasets: [
        {
          label: "Completion",
          data: weeklyCompletion.values,
          borderColor: "#6d4aff",
          backgroundColor: gradient,
          pointBackgroundColor: "#ffffff",
          pointBorderColor: "#6d4aff",
          pointBorderWidth: 3,
          pointHoverRadius: 7,
          pointRadius: 5,
          borderWidth: 4,
          fill: true,
          tension: 0.42,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "#191825",
          borderColor: "rgba(255, 255, 255, 0.12)",
          borderWidth: 1,
          bodyFont: {
            weight: "700",
          },
          callbacks: {
            label(context) {
              return `${context.parsed.y}% completed`;
            },
          },
          displayColors: false,
          padding: 12,
        },
      },
      scales: {
        x: {
          border: {
            display: false,
          },
          grid: {
            display: false,
          },
          ticks: {
            color: "#6f6a7c",
            font: {
              weight: "800",
            },
          },
        },
        y: {
          beginAtZero: true,
          max: 100,
          border: {
            display: false,
          },
          grid: {
            color: "#efedf6",
          },
          ticks: {
            color: "#6f6a7c",
            callback(value) {
              return `${value}%`;
            },
            font: {
              weight: "700",
            },
            stepSize: 25,
          },
        },
      },
      interaction: {
        intersect: false,
        mode: "index",
      },
    },
  });
} else if (chartCanvas) {
  drawFallbackLineChart(chartCanvas, weeklyCompletion);

  window.addEventListener("resize", () => {
    drawFallbackLineChart(chartCanvas, weeklyCompletion);
  });
}
