var xhr = null;
msg_getter = document.getElementById("get-message")
msg_getter.addEventListener("click", fetchData('http://127.0.0.1:5000/message', 'result-container', false));
msg_getter.addEventListener("click", getDate);
window.addEventListener("load", fetchData('http://127.0.0.1:5000/stream', 'data', true));


function getDate() {
    date = new Date().toString();
    document.getElementById('time-container').textContent = date;
}


function fetchData(address, eid, streaming) {
    return async function(e) {
        const response = await fetch(address);

        if (!response.ok) {
            console.error('Network response was not ok');
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        const dataDisplay = document.getElementById(eid);

        do {
            const { done, value } = await reader.read();

            if (done) {
                console.log('Stream finished.');
                break;
            }

            const data = decoder.decode(value, { stream: streaming });
            dataDisplay.innerHTML = data;
        } while ( streaming );
    }
}