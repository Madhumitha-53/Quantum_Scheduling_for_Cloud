async function addTask() {
    const cpu = document.getElementById("cpu").value;
    const memory = document.getElementById("memory").value;
    const sla = document.getElementById("sla").value;

    const res = await fetch("/tasks", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ cpu: parseInt(cpu), memory: parseInt(memory), sla: parseInt(sla) })
    });

    const data = await res.json();
    alert(data.message);
    loadTasks();
}

async function loadTasks() {
    const res = await fetch("/tasks");
    const tasks = await res.json();

    const stack = document.getElementById("stack");
    stack.innerHTML = "";

    tasks.forEach(t => {
        stack.innerHTML += `<div>Task ${t.id} | CPU ${t.cpu} | SLA ${t.sla}</div>`;
    });
}

async function allocate() {
    const res = await fetch("/allocate", { method: "POST" });
    const data = await res.json();

    document.getElementById("output").innerText =
        JSON.stringify(data, null, 2);

    loadTasks();
}

window.onload = loadTasks;