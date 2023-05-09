let port;
let idle = true;

/**
 * This function is called when a message is received from the content script. It sends the message to the server and waits for a response. When the response is received, it sends it back to the content script.
 * @param {*} msg 
 * @returns 
 */
function messageHandler(msg){
    if (!idle){
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open('GET', "http://localhost:8080?msg="+JSON.stringify(msg));
    xhr.onreadystatechange = function() {
       if (xhr.readyState == XMLHttpRequest.DONE) {
          idle = true;
          var jsonResponse = JSON.parse(xhr.responseText);
          port.postMessage(jsonResponse);
       }
    }
    idle = false;
    xhr.send();
}

/**
 * Called when the content script connects to the background script. It saves the port for later use.
 * @param {*} p 
 */
function connect(p){
    port = p;
    port.onMessage.addListener(messageHandler);
}

browser.runtime.onConnect.addListener(connect);