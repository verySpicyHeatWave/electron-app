msg_getter = document.getElementById("get-message")
msg_getter.addEventListener("click", fetchData("http://127.0.0.1:5000/message", "result-container", false));
msg_getter.addEventListener("click", getDate);
window.addEventListener("load", fetchData("http://127.0.0.1:5000/stream", "data", true));

var msg_count = 0;
var msg_timeout = 0;

function getDate() {
    date = new Date().toString();
    document.getElementById("time-container").textContent = date;
}


function fetchData(address, eid, streaming) {
    return async function(e) {
        const response = await fetch(address);

        if (!response.ok) {
            console.error("Network response was not ok");
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        const dataDisplay = document.getElementById(eid);

        do {
            const { done, value } = await reader.read();

            if (done) {
                console.log("Stream finished.");
                break;
            }

            const data = decoder.decode(value, { stream: streaming });
            dataDisplay.innerHTML = data;
            determineState(data);
            getDate();
        } while ( streaming );
    } //"Uncaught (in promise) TypeError: Failed to fetch" when the server resets without the GUI resetting -- how to handle?
}


function determineState(data) {
    if (data.includes("battery_pn")) {
        receiving = true;
        document.getElementById("main-css").href = "styles.css"
        msg_count += 1;
        pack_form(data)
    }
    else {
        receiving = false;
        msg_timeout += 1;
        // document.getElementById("main-css").href = "styles_timeout.css"
    }
}


function pack_form(data) {
    obj = JSON.parse(data.replace("Data: ", ""));
    document.getElementById("pack-voltage").innerHTML = obj.pack_voltage.toFixed(3).concat("V");
    document.getElementById("pack-current").innerHTML = obj.pack_current.toFixed(3).concat("A");
    document.getElementById("cell1-voltage").innerHTML = obj.cell1_voltage.toFixed(3).concat("V");
    document.getElementById("cell2-voltage").innerHTML = obj.cell2_voltage.toFixed(3).concat("V");
    document.getElementById("cell3-voltage").innerHTML = obj.cell3_voltage.toFixed(3).concat("V");
    document.getElementById("cell4-voltage").innerHTML = obj.cell4_voltage.toFixed(3).concat("V");
    document.getElementById("cell5-voltage").innerHTML = obj.cell5_voltage.toFixed(3).concat("V");
    document.getElementById("cell6-voltage").innerHTML = obj.cell6_voltage.toFixed(3).concat("V");
    document.getElementById("cell7-voltage").innerHTML = obj.cell7_voltage.toFixed(3).concat("V");
    document.getElementById("cell8-voltage").innerHTML = obj.cell8_voltage.toFixed(3).concat("V");
    document.getElementById("cell-average").innerHTML = obj.cell_average.toFixed(3).concat("V");
    document.getElementById("cell-range").innerHTML = obj.cell_range.toFixed(3).concat("V");
    document.getElementById("pack1-temp").innerHTML = obj.pack_temp.toString().concat("°C");
    document.getElementById("pack2-temp").innerHTML = obj.pack_temp.toString().concat("°C");
    document.getElementById("bms-temp").innerHTML = obj.bms_temp.toString().concat("°C");
    document.getElementById("cfet-temp").innerHTML = obj.cfet_temp.toString().concat("°C");
    document.getElementById("dfet-temp").innerHTML = obj.dfet_temp.toString().concat("°C");
    document.getElementById("pcba-temp").innerHTML = obj.board_temp.toString().concat("°C");
}