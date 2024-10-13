function startStream() {
    const eventSource = new EventSource('http://127.0.0.1:5000/stream');
    eventSource.onmessage = function(event) {
        dataDiv = document.getElementById('result-container');
        dataDiv.innerHTML = event.data;
    };
}