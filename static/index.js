socket.on("kick", () => location.reload())
socket.on("begin", () => {
    const f = document.querySelector(".check");
    f.style.display = "block";
    f.textContent = "Подготовка к началу игры..."
});

socket.on("run", () => {
    location.reload();
})

const k = document.querySelector(".kladform")
if (k) {
    const t = document.getElementById("klad");
    t.value = "";
    k.addEventListener("submit", event => {
        event.preventDefault();
        socket.emit("klad", { klad: t.value }, (r) => {
            alert(`${r.status == "error" ? "Неверный клад или такой был" : "Ура!! Верно"}, осталось кладов ${r.left}/5`);
            if (r.left == 0) location.reload();
        });
        t.value = "";
    })
}