let data = [];
const doEvents = () => {
    addEventListenerMulti(document.getElementsByClassName("kick"), "click", e => {
        socket.emit("kick", { ip: e.target.dataset.ip }, r => {
            if (r != "ok") alert("Ошибка при изгнании");
        })
    });
    document.getElementById("begin").disabled = data.length == 0;
    if (document.querySelector("tbody").innerHTML.length > 0) {
        document.getElementById("begin").disabled = false;
    }

}
const update = data_new => {
    data = data_new
    document.querySelector("tbody").innerHTML = data.map(t => `
        <tr><td>${t.ip}</td><td>${t.pc}</td><td>${t.name}</td><td>${t.klads ? (t.klads ?? []).length : ""}</td><td><button data-ip="${t.ip}" class="kick">Изгнать</button></td></tr>
    `).join("\n");
    doEvents();
}

socket.on("pcchange", update);
doEvents();
const statusF = document.querySelector(".check");

document.querySelector("#begin").addEventListener("click", () => {
    statusF.textContent = "Подготовка...";
    socket.emit("begin");
});

socket.on("run", ()=>statusF.textContent="Игра идёт")