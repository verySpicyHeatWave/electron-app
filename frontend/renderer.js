let msg_getter = document.getElementById("get-message")
msg_getter.addEventListener("click", fetchData("http://127.0.0.1:5000/message", "result-container", false));
msg_getter.addEventListener("click", getDate);
window.addEventListener("load", fetchData("http://127.0.0.1:5000/stream", "data", true));
document.getElementById("msg-counters").addEventListener("dblclick", resetCounters);

var msg_count = 0;
var msg_timeout = 0;

function getDate() {
    const date = new Date().toString();
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
            if (determineMsgState(data)) {
                pack_form(data);
            }
            getDate();
        } while ( streaming );
    } //"Uncaught (in promise) TypeError: Failed to fetch" when the server resets without the GUI resetting -- how to handle?
}


function determineMsgState(data) {
    if (data.includes("battery_pn")) {
        msg_count += 1;
        document.getElementById("msg-count").innerHTML = msg_count;
        document.getElementById("main-css").href = "styles.css";
        return true;
    }
    else {
        msg_timeout += 1;
        document.getElementById("msg-timeouts").innerHTML = msg_timeout;
        // document.getElementById("main-css").href = "styles_timeout.css"
        return false;
    }
}


function pack_form(data) {
    const obj = JSON.parse(data.replace("Data: ", ""));
    const cellElems = createCellElementsArray();
    cellElems[0].innerHTML = obj.cell1_voltage.toFixed(3).concat("V");
    cellElems[1].innerHTML = obj.cell2_voltage.toFixed(3).concat("V");
    cellElems[2].innerHTML = obj.cell3_voltage.toFixed(3).concat("V");
    cellElems[3].innerHTML = obj.cell4_voltage.toFixed(3).concat("V");
    cellElems[4].innerHTML = obj.cell5_voltage.toFixed(3).concat("V");
    cellElems[5].innerHTML = obj.cell6_voltage.toFixed(3).concat("V");
    cellElems[6].innerHTML = obj.cell7_voltage.toFixed(3).concat("V");
    cellElems[7].innerHTML = obj.cell8_voltage.toFixed(3).concat("V");
    highlightMinMaxCells(obj, cellElems);

    document.getElementById("pack-voltage").innerHTML = obj.pack_voltage.toFixed(3).concat("V");
    document.getElementById("pack-current").innerHTML = obj.pack_current.toFixed(3).concat("A");
    document.getElementById("cell-average").innerHTML = obj.cell_average.toFixed(3).concat("V");
    document.getElementById("cell-range").innerHTML = obj.cell_range.toFixed(3).concat("V");
    document.getElementById("pack1-temp").innerHTML = obj.pack_temp.toString().concat("°C");
    document.getElementById("pack2-temp").innerHTML = obj.pack_temp.toString().concat("°C");
    document.getElementById("bms-temp").innerHTML = obj.bms_temp.toString().concat("°C");
    document.getElementById("cfet-temp").innerHTML = obj.cfet_temp.toString().concat("°C");
    document.getElementById("dfet-temp").innerHTML = obj.dfet_temp.toString().concat("°C");
    document.getElementById("pcba-temp").innerHTML = obj.board_temp.toString().concat("°C");
    document.getElementById("part-number").innerHTML = obj.battery_pn.toString();
    document.getElementById("serial-number").innerHTML = "SN".concat(obj.battery_sn.toString());
    colorStatusBits(obj);
}


function resetCounters() {
    msg_count = 0;
    msg_timeout = 0;
    document.getElementById("msg-count").innerHTML = msg_count;
    document.getElementById("msg-timeouts").innerHTML = msg_timeout;
}


function highlightMinMaxCells(obj, elems) {
    let min = -1;
    let minv = 5;
    let max = -1;
    let maxv = 0;

    const cells = createCellVoltagesArray(obj);
    for (let i = 0; i < cells.length; i++) {
        if (cells[i] > maxv) {
            maxv = cells[i];
            max = i;
        }
        if (cells[i] < minv) {
            minv = cells[i];
            min = i;
        }
    }

    for (let i = 0; i < elems.length; i++) {
        if (i == min) {
            elems[i].style.backgroundColor = "#de918c";
        }
        else if (i == max) {
            elems[i].style.backgroundColor = "#92db88";
        }
        else {
            elems[i].style.backgroundColor = ""
        }
    }
}


function createCellVoltagesArray(obj) {
    let cells = [
        obj.cell1_voltage, obj.cell2_voltage,
        obj.cell3_voltage, obj.cell4_voltage,
        obj.cell5_voltage, obj.cell6_voltage, 
        obj.cell7_voltage, obj.cell8_voltage];
    return cells;    
}

function createCellElementsArray() {
    let cellElements = [
        document.getElementById("cell1-voltage"),
        document.getElementById("cell2-voltage"),
        document.getElementById("cell3-voltage"),
        document.getElementById("cell4-voltage"),
        document.getElementById("cell5-voltage"),
        document.getElementById("cell6-voltage"),
        document.getElementById("cell7-voltage"),
        document.getElementById("cell8-voltage")];
    return cellElements;
}


function colorStatusBits(obj) {
    console.log("BCOBB: To-Do!")
}