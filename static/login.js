const button = document.querySelector("button");
document.querySelector("form").addEventListener("submit", async e=>{
    e.preventDefault();
    button.disabled = true;
    document.querySelector(".check").style.display="block";
    socket.emit("newpc", {pc:document.querySelector("#pc-number").value, name:document.querySelector("#name").value}, response=>{
        if(response == "ok") location.reload();
        else document.querySelector(".check").textContent="Ошибка"
    })
});