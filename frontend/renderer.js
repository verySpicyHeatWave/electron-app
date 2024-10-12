var xhr = null;
document.getElementById("get-message").addEventListener("click", getMessage);

getXmlHttpRequestObject = function () {
    if (!xhr) {
        // Create a new XMLHttpRequest object 
        xhr = new XMLHttpRequest();
    }
    return xhr;
};

function dataCallback() {
    // Check response is ready or not
    if (xhr.readyState == 4 && xhr.status == 200) {
        console.log("User data received!");
        getDate();
        dataDiv = document.getElementById('result-container');
        // Set current data text
        dataDiv.innerHTML = xhr.responseText;
    }
}
function getMessage() {
    console.log("Get message...");
    xhr = getXmlHttpRequestObject();
    xhr.onreadystatechange = dataCallback;
    // asynchronous requests
    xhr.open("GET", "http://127.0.0.1:5000/message", true);
    // Send the request over the network
    xhr.send(null);
}
function getDate() {
    date = new Date().toString();

    document.getElementById('time-container').textContent
        = date;
}
(function () {
    getDate();
})();