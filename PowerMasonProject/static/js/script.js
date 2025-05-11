document.addEventListener("DOMContentLoaded", () => {
  const navItems = document.querySelectorAll(".nav-item");
  const contentContainer = document.getElementById("content");
  const header = document.querySelector("header");

  function activateTab(tab, redirectUrl) {
    if (!tab) return;

    navItems.forEach((item) => {
      item.classList.toggle("active", item.dataset.tab === tab);
      item.setAttribute(
        "aria-pressed",
        item.dataset.tab === tab ? "true" : "false"
      );
    });

    const activeItem = Array.from(navItems).find(
      (item) => item.dataset.tab === tab
    );
    if (activeItem) {
      header.textContent = activeItem.title || "Default Header";
    }

    // Load partial content via AJAX
    if (redirectUrl) {
      fetch(redirectUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then((response) => response.text())
        .then((html) => {
          contentContainer.innerHTML = html;
          history.pushState({ tab }, "", redirectUrl);
        })
        .catch((err) => {
          console.error(err);
          contentContainer.innerHTML = "<p>Error loading content.</p>";
        });
    }
  }

  navItems.forEach((item) => {
    const tab = item.dataset.tab;
    const redirectUrl = item.dataset.url;

    item.addEventListener("click", () => activateTab(tab, redirectUrl));
    item.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        item.click();
      }
    });
  });

  // Handle back/forward buttons
  window.addEventListener("popstate", (e) => {
    const tab = e.state?.tab;
    const activeItem = Array.from(navItems).find((i) => i.dataset.tab === tab);
    const redirectUrl = activeItem?.dataset.url;
    if (tab && redirectUrl) {
      activateTab(tab, redirectUrl);
    }
  });

  // Initialize default tab
  activateTab(
    "dashboard",
    document.querySelector('[data-tab="dashboard"]').dataset.url
  );

  // Get references to DOM elements
  const fileInput = document.getElementById("fileInputSection1");
  const projectTableBody = document.getElementById("projectListTableBody");

  // Attach event listener to the hidden file input
  fileInput.addEventListener("change", handleFileUpload);

  // Trigger file input when the New Project button is clicked
  document.querySelector(".btnNewProject").addEventListener("click", () => {
    fileInput.click();
  });

  function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: "array" });
      const sheetName = workbook.SheetNames[0]; // Get the first sheet
      const sheet = workbook.Sheets[sheetName];
      const projects = XLSX.utils.sheet_to_json(sheet); // Convert sheet to JSON
      updateProjectTable(projects);
    };
    reader.readAsArrayBuffer(file);
  }

  function updateProjectTable(projects) {
    // Track existing project names
    const existingProjectNames = new Set();
    document
      .querySelectorAll("#projectListTableBody tr td:first-child")
      .forEach((cell) => {
        existingProjectNames.add(cell.textContent.trim());
      });

    projects.forEach((project) => {
      const { Name, Start, End, Budget, Expenses, Progress } = project;

      // Check if the project name already exists
      if (existingProjectNames.has(Name)) {
        const overwrite = confirm(
          `Project "${Name}" is already displayed on the web. Do you want to overwrite it?`
        );
        if (!overwrite) return;

        // Remove the existing row with the same project name
        const existingRow = Array.from(
          projectTableBody.querySelectorAll("tr")
        ).find(
          (row) =>
            row.querySelector("td:first-child").textContent.trim() === Name
        );
        if (existingRow) {
          existingRow.remove();
        }
      }

      // Add the project to the set
      existingProjectNames.add(Name);

      // Calculate new status
      const newStatus = calculateStatus(
        parseFloat(Budget),
        parseFloat(Expenses),
        parseFloat(Progress),
        End
      );

      // Create a new table row
      const row = document.createElement("tr");
      row.tabIndex = 0;
      row.innerHTML = `  
      <td>${Name}</td>
      <td><span class="status-tag ${getStatusClass(
        newStatus
      )}">${newStatus}</span></td>
      <td>${Start}</td>
      <td>${End}</td>
      <td>${formatCurrency(Budget)}</td>
      <td>${formatCurrency(Expenses)}</td>
      <td>${Progress}</td>
      <td>
        <button
          class="updateButton"
          aria-label="Update ${Name}"
        >
          Update
        </button>
      </td>
    `;
      projectTableBody.appendChild(row);
    });
  }

  function calculateStatus(budget, expenses, progress, endDate) {
    const today = new Date();
    const end = new Date(endDate);
    const remainingDays = (end - today) / (1000 * 60 * 60 * 24); // Convert milliseconds to days

    if (progress === 100) return "Completed";
    if (expenses > budget) return "Budget Overrun";
    if (progress < 50 && remainingDays < 14) return "Delayed"; // Low progress and less than 2 weeks left
    return "On Track";
  }

  function getStatusClass(status) {
    return (
      {
        Completed: "status-completed",
        "Budget Overrun": "status-delayed",
        Delayed: "status-delayed",
        "On Track": "status-ontrack",
      }[status] || "status-unknown"
    );
  }

  function formatCurrency(value) {
    return new Intl.NumberFormat("en-PH", {
      style: "currency",
      currency: "PHP",
    }).format(value);
  }

  const expenseForm = document.getElementById("expenseForm");
  const expensesList = document.getElementById("expensesList");
  const expenses = [];

  if (expenseForm) {
    expenseForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const date = expenseForm.expenseDate.value;
      const desc = expenseForm.expenseDescription.value.trim();
      const amount = parseFloat(expenseForm.expenseAmount.value);
      const category = expenseForm.expenseCategory.value;

      if (!date || !desc || isNaN(amount) || amount <= 0 || !category) {
        alert("Please fill all expense fields correctly.");
        return;
      }

      expenses.push({ date, desc, amount, category });
      updateExpensesDisplay();
      expenseForm.reset();
    });
  }

  function updateExpensesDisplay() {
    if (expenses.length === 0) {
      expensesList.textContent = "No expenses recorded yet.";
      return;
    }

    let html = "Expenses:\n";
    expenses.forEach((exp, i) => {
      html += `${i + 1}. ${exp.date} - ${exp.desc} [${
        exp.category
      }] : ₱${exp.amount.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}\n`;
    });

    expensesList.textContent = html;
  }

  updateExpensesDisplay();

  const estimationForm = document.getElementById("estimationForm");
  const estimationResult = document.getElementById("estimationResult");

  if (estimationForm) {
    estimationForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const cost = parseFloat(estimationForm.historicalCost.value);
      const duration = parseInt(estimationForm.historicalDuration.value, 10);
      const factorPct = parseFloat(estimationForm.adjustmentFactor.value);

      if (isNaN(cost) || isNaN(duration) || isNaN(factorPct)) {
        alert("Please enter valid numbers.");
        return;
      }

      const adjCost = cost + cost * (factorPct / 100);
      const adjDuration = Math.round(duration + duration * (factorPct / 100));

      estimationResult.textContent = `Estimated Cost: ₱${adjCost.toLocaleString(
        undefined,
        { maximumFractionDigits: 2 }
      )}\nEstimated Duration: ${adjDuration} days`;
    });
  }

  // The report generation part
  const reportTypeSelect = document.getElementById("reportTypeSelect");
  const generateReportBtn = document.getElementById("generateReportBtn");
  const printReportBtn = document.getElementById("printReportBtn");
  const reportOutput = document.getElementById("reportOutput");

  // Handle Generate Report button click
  if (generateReportBtn && reportTypeSelect && reportOutput) {
    generateReportBtn.addEventListener("click", () => {
      const selectedReportType = reportTypeSelect.value;
      let reportContent = "";

      switch (selectedReportType) {
        case "project-status":
          reportContent = generateProjectStatusReport();
          break;
        case "financial-performance":
          reportContent = generateFinancialPerformanceReport();
          break;
        case "resource-utilization":
          reportContent = generateResourceUtilizationReport();
          break;
        default:
          reportContent = "Invalid report type selected.";
          break;
      }

      // Display the generated report in the output area
      reportOutput.textContent = reportContent;
    });
  }

  // Handle Print Report button click
  let printWindow = null; // Declare the window outside the event handler so it doesn't open multiple times.

  if (printReportBtn && reportOutput) {
    printReportBtn.addEventListener("click", () => {
      const reportContent = reportOutput.textContent.trim();
      if (!reportContent) {
        alert("No report to print. Please generate a report first.");
        return;
      }

      if (!printWindow || printWindow.closed) {
        printWindow = window.open("", "_blank");

        // Get the current date and time
        const currentDate = new Date();
        const dateString = `${
          currentDate.getMonth() + 1
        }/${currentDate.getDate()}/${currentDate.getFullYear()} ${currentDate.getHours()}:${currentDate.getMinutes()}:${currentDate.getSeconds()}`;

        // Add content and styles once if the window is not already opened
        printWindow.document.write(`
        <html>
          <head>
            <title>Report</title>
            <style>
              body { font-family: Arial, sans-serif; font-size: 14px; }
              h1 { font-size: 18px; }
              pre { white-space: pre-wrap; word-wrap: break-word; }
              footer { font-size: 12px; text-align: right; margin-top: 20px; }
            </style>
          </head>
          <body>
            <h1>Report - Generated on ${dateString}</h1>
            <pre>${reportContent}</pre>
            <footer>Generated by Your App</footer>
          </body>
        </html>
        `);

        printWindow.document.close();
        printWindow.print();
      } else {
        printWindow.print();
      }
    });
  }
});
