let port;
let formElement;
let user;
let password;
let infoBox;
let statusIndicator;



var cssStyle = ".bci-button{border-radius: 3px;border-style: none;box-sizing: border-box;background-color: #2196f3;color: #fff;padding: 3px;font-size: 18px;line-height: 18px;box-shadow: rgba(0, 0, 0, 0.4) 0px 3px 5px;cursor: pointer;}.bci-button:hover{background-color: #1872ba;}.bci-button:onclick{background-color: #0985e8;}.indicator-center,.info{box-sizing:border-box;left:50%;position:fixed;text-align:center;top:50%}.bci-cross{-webkit-animation:.35s cross;background:#b50e18;background:radial-gradient(circle,rgba(181,14,24,.6) 0,rgba(181,14,24,.6) 0);color:#fff}.bci-load{-webkit-animation:1s ease-in-out infinite spin;border:6px solid rgba(150,150,150,.4);border-radius:50%;border-top:6px solid #fff}.bci-tick{-webkit-animation:.35s tick;background:#0daf2f;background:radial-gradient(circle,rgba(13,175,47,.6) 0,rgba(13,175,47,.6) 0);color:#fff}.indicator-center{z-index:10000;border-radius:50%;font-size:62px;height:100px;line-height:100px;margin-left:-50px;margin-top:-50px;width:100px}.info{z-index:1000;backdrop-filter:blur(6px);background-color:rgba(0,0,0,.3);border-radius:20px;font-size:60pt;height:250px;line-height:250px;margin-left:-125px;margin-top:-125px;width:250px}@keyframes spin{to{-webkit-transform:rotate(360deg)}}@keyframes tick{0%{background:radial-gradient(circle,rgba(13,175,47,0) 100%,rgba(13,175,47,.6) 100%)}10%{background:radial-gradient(circle,rgba(13,175,47,0) 90%,rgba(13,175,47,.6) 90%)}20%{background:radial-gradient(circle,rgba(13,175,47,0) 80%,rgba(13,175,47,.6) 80%)}30%{background:radial-gradient(circle,rgba(13,175,47,0) 70%,rgba(13,175,47,.6) 70%)}40%{background:radial-gradient(circle,rgba(13,175,47,0) 60%,rgba(13,175,47,.6) 60%)}50%{background:radial-gradient(circle,rgba(13,175,47,0) 50%,rgba(13,175,47,.6) 50%)}60%{background:radial-gradient(circle,rgba(13,175,47,0) 40%,rgba(13,175,47,.6) 40%)}70%{background:radial-gradient(circle,rgba(13,175,47,0) 30%,rgba(13,175,47,.6) 30%)}80%{background:radial-gradient(circle,rgba(13,175,47,0) 20%,rgba(13,175,47,.6) 20%)}90%{background:radial-gradient(circle,rgba(13,175,47,0) 10%,rgba(13,175,47,.6) 10%)}100%{background:radial-gradient(circle,rgba(13,175,47,0) 0,rgba(13,175,47,.6) 0)}}@keyframes cross{0%{background:radial-gradient(circle,rgba(181,14,24,0) 100%,rgba(181,14,24,.6) 100%)}10%{background:radial-gradient(circle,rgba(181,14,24,0) 90%,rgba(181,14,24,.6) 90%)}20%{background:radial-gradient(circle,rgba(181,14,24,0) 80%,rgba(181,14,24,.6) 80%)}30%{background:radial-gradient(circle,rgba(181,14,24,0) 70%,rgba(181,14,24,.6) 70%)}40%{background:radial-gradient(circle,rgba(181,14,24,0) 60%,rgba(181,14,24,.6) 60%)}50%{background:radial-gradient(circle,rgba(181,14,24,0) 50%,rgba(181,14,24,.6) 50%)}60%{background:radial-gradient(circle,rgba(181,14,24,0) 40%,rgba(181,14,24,.6) 40%)}70%{background:radial-gradient(circle,rgba(181,14,24,0) 30%,rgba(181,14,24,.6) 30%)}80%{background:radial-gradient(circle,rgba(181,14,24,0) 20%,rgba(181,14,24,.6) 20%)}90%{background:radial-gradient(circle,rgba(181,14,24,0) 10%,rgba(181,14,24,.6) 10%)}100%{background:radial-gradient(circle,rgba(181,14,24,0) 0,rgba(181,14,24,.6) 0)}}"

var inlineButton=`KeyWave`

/**
 * Remove status indicator from InfoBox.
 */
function RemoveStatusIndicator(){
    if(statusIndicator){
        statusIndicator.remove();
    }
    statusIndicator = null;
}

/**
 * Remove infobox and indicator from web site.
 */
function RemoveInfoBox(){
    RemoveStatusIndicator()
    if(infoBox){
        infoBox.remove();
    }
    infoBox = null;
}

/**
 * Remove InfoBox after given amount of ms.
 * @param {*} ms 
 */
async function DelayedRemoveInfoBox(ms){
    await new Promise(done => setTimeout(() => done(), ms));
    RemoveInfoBox();
}

/**
 * Submit after UX animation is done.
 * @param {Time in ms before removal of InfoBox.} ms 
 */
async function DelayedSubmit(ms){
    DelayedRemoveInfoBox(ms);
    formElement.submit();
}

/**
 * Add info box along loading spinner to website to indicate something happening.
 */
function AddInfoBox(){
    RemoveInfoBox();

    infoBox = document.createElement("div");
    infoBox.classList.add("info");
    document.body.appendChild(infoBox);

    statusIndicator = document.createElement("div");
    statusIndicator.classList.add("bci-load");
    statusIndicator.classList.add("indicator-center");
    document.body.appendChild(statusIndicator);
}

/**
 * Show confirmation indicator after successful login.
 */
function ShowConfirmation(){
    if(!infoBox){
        AddInfoBox();
    }
    RemoveStatusIndicator();

    statusIndicator = document.createElement("div");
    statusIndicator.classList.add("bci-tick");
    statusIndicator.classList.add("indicator-center");
    statusIndicator.innerText = "✓";
    document.body.appendChild(statusIndicator);
}

/**
 * Display Error Cross on web page after failed login attempt.
 */
function ShowErrorCross(){
    if(!infoBox){
        AddInfoBox();
    }
    RemoveStatusIndicator();

    statusIndicator = document.createElement("div");
    statusIndicator.classList.add("bci-cross");
    statusIndicator.classList.add("indicator-center");
    statusIndicator.innerText = "⨯";
    document.body.appendChild(statusIndicator);
}

/**
 * Finds input for either user name of password in current form context.
 * Depth-First-Search.
 * @param {HTMLElement} formElement root element to start search from.
 * @returns UserInput if found, else null.
 */
 function FindUserInput(formElement){
    for (let i = 0; i < formElement.children.length; i++) {
        let child = formElement.children[i];
        if (child.nodeName == "INPUT" && (child.type == "email" || child.type == "text")) {
            return child;
        }
        let result = FindUserInput(child);
        if(result){
            return result;
        }
    }
   return null;
}

/**
 * Finds password input on current website.
 * @returns First password input on website.
 */
function FindPasswordInput(){
    let inputs = document.getElementsByTagName("input");
    for (let i = 0; i < inputs.length; i++) {
        let input = inputs[i];
        if(input.type == "password"){
            return input;
        }
    }
    return null;
}

/**
 * Adds button for BCI authentication if 
 */
function CreateBCIButton(){
    let style = document.createElement("style");
    style.innerText = cssStyle;
    document.head.appendChild(style);

    let button = document.createElement("button");
    button.innerHTML = inlineButton;
    button.classList.add("bci-button");
    button.addEventListener("click",function(ev){
        ev.preventDefault();
        AddInfoBox();
        port.postMessage({"type": "auth", "domain": window.location.hostname})
    });
    formElement.appendChild(button);
}

/**
 * Finds encapsulating form element for given element.
 * @param {HTMLNode} htmlElement Start element for search.
 * @returns Parent form element. If not found, returns null.
 */
function GetParentForm(htmlElement){
    let form = htmlElement.parentNode;
    while (form.nodeName != "FORM") {
        form = form.parentNode;
        if (form.nodeName == "BODY"){
            return null;
        }
    }
    return form;
}

async function lateLoad(i){
    if (formElement){
        return;
    }
    if (i == 10){
        return;
    }
    await new Promise(done => setTimeout(() => done(), 500));
    addBci();
    lateLoad(i+1);
}

/**
 * Add BCI button to website. Only if login form is present.
 * @returns 
 */
function addBci(){
    password = FindPasswordInput();
    if(!password){
        console.log("Could not find password input!");
        return;
    }

    formElement = GetParentForm(password);
    if(!formElement){
        console.log("Could not find parent form elements!");
        return;
    }
    console.log("Found form element!");

    CreateBCIButton();

    user = FindUserInput(formElement);
    if(!user){
        console.log("Could not find user name input!");
        return;
    }
    console.log("Found user name element!");
}

/**
 * Message handler for background script.
 * @param {Object} msg Message received from background script.
 */
async function messageHandler(msg){
    console.log(msg);
    msg = msg["resp"];
    console.log(msg);
    switch(msg["type"]){
        case "check":
            if (msg["is_present"]){
                addBci();
                // Check for 5 seconds if not find a login after some waiting
                lateLoad(1);
            }
            break;
        case "auth":
            user.value = msg["username"];
            password.value = msg["password"];
            ShowConfirmation();
            DelayedSubmit(600);
            break;
        case "auth_fail":
            ShowErrorCross();
            DelayedRemoveInfoBox(600);
    }
}

/**
 * Main function of content script. Connects to background script and checks if login form is present.
 */
function main(){
    console.log("Started addon");


    port = browser.runtime.connect()
    port.onMessage.addListener(messageHandler);
    console.log("Connected to background script");
    
    var domain = window.location.hostname;
    port.postMessage({"type": "check", "domain": domain})
}

main();