window.addEventListener('DOMContentLoaded', () => {

    document.getElementById("input-box-ok").addEventListener("click", () => {
        const exchange = document.getElementById("exchange-input").value;
        window.resp.sendToMain(exchange);
        window.close();
    });

    document.getElementById("input-box-cancel").addEventListener("click", () => {
        window.resp.sendToMain(null);
        window.close();
    });
  });


