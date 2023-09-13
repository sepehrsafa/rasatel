
const messageBoxElement = document.getElementById("messageBox")
const messageBoxPage = document.getElementById("messageBoxPage")
const messagePage = document.getElementById("messagePage")
const messageSection = document.getElementById("messageSection")
const smsContent = document.getElementById("smsContent");
const chatBoxContent = document.getElementById("chatBoxContent");
const sendSMS = document.getElementById("sendMessageButton");
const textMessageInput = document.getElementById("textMessageInput");
const chatWindowName = document.getElementById("chatWindowName")
var messageBoxes = []
var latestMessageBox;
var oldestMessageBox;
var latestMessage;
var oldestMessage;
var updateMessagesIntervalID;
var updateMessageBoxesIntervalID
var currentMessageBox;
var oldRetrieveMessageBoxesInProcess = false
var getOlderMessagesInProcess = false

async function postData(url = '', data) {
    console.log(JSON.stringify(data))
    // Default options are marked with *
    const response = await fetch(url, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            // 'Content-Type': 'application/x-www-form-urlencoded',
          },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'origin', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url

        body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
}

async function getData(url = '') {
    // Default options are marked with *
    const response = await fetch(url, {
        method: 'GET', // *GET, POST, PUT, DELETE, etc.
        mode: 'cors', // no-cors, *cors, same-origin
        cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
        },
        redirect: 'follow', // manual, *follow, error
        referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    });
    return response.json(); // parses JSON response into native JavaScript objects
}


function messageBoxParser(box){
        var name
        if(box['contact']){
            name = `${box['contact']['firstname']} ${box['contact']['lastname']}`
        }
        else{
            name = box['number']
        }
        console.log(box)
        let time = new Date(box['messages'][0]['timestamp'])
        //format with just the time if today, else format with date and time
        if(time.toDateString() == new Date().toDateString()){
            time = time.toLocaleTimeString()
        }
        else{
            time = time.toLocaleString()
        }
        //class=read
        let read = box['read'] ? '' : 'avatar-online'
            
        var text = `
        <a onclick="javascript:showMessages('${box['id']}','${box['number']}','${name}');">
            <div class="avatar ${read}" id='read-${box['id']}'>
                <img src=/static/sms/assets/img/avatar2.png width="48" alt="">
            </div>
            <div class="person-list-body">
                <div>
                    <h5>${name}</h5>
                    <p>${box['messages'][0]['message']}</p>
                </div>
                <div class="last-chat-time"><small class="text-muted">${time}</small></div>
            </div>
        </a>
    `
        let li = document.createElement("li");
        li.setAttribute("id", box['id']);
        li.setAttribute("class", "person-list-item col-12");
        li.innerHTML = text.trim();
        return li

}

function retrieveMessageBoxes() {
    
    url = '/api/sms/retrieve/port/'+port+'/messageboxes/'+requestuuid
    getData(url).then(data =>{
        latestMessageBox = data[0]['messages'][0]['id']
        oldestMessageBox = data[data.length-1]['messages'][0]['id']
        for(const box of data){
            li = messageBoxParser(box)
            messageBoxElement.append(li);
        }
        //updateRetrieveMessageBoxesInterval(1)
    })
}

function updateRetrieveMessageBoxesInterval(action,time=5000){
    if (action==1){
        updateMessageBoxesIntervalID = setInterval(updateRetrieveMessageBoxes, time);
    }
    else if (action==2){
        clearInterval(updateMessageBoxesIntervalID)
    }
}


function updateRetrieveMessageBoxes(){
    getData('/api/sms/update/retrieve/port/'+port+'/messageboxes/'+requestuuid+'/2/'+latestMessageBox).then(data =>{
        if(data.length>0){
            latestMessageBox = data[0]['messages'][0]['id']
            data = data.reverse()
            for(const box of data){
                oldBox = document.getElementById(box['id'])
                if(oldBox){
                    oldBox.remove()
                }
                li = messageBoxParser(box)
                messageBoxElement.prepend(li);
                
            }
        }
    })
}

function oldRetrieveMessageBoxes(){
    getData('/api/sms/update/retrieve/port/'+port+'/messageboxes/'+requestuuid+'/1/'+latestMessageBox).then(data =>{
        if(data.length>0){
            data = data.reverse()
            oldestMessageBox = data[0]['messages'][0]['id']
            
            for(const box of data){

                li = messageBoxParser(box)
    
                messageBoxElement.append(li);
            }
        }
        oldRetrieveMessageBoxesInProcess = false
    }
)}

function messageParser(message){



    if(message['messageType']==1){
    let= internalClass = "receive"
    let= internalfloat = "left"
    }
    else{
    internalClass = "send"
    internalfloat = "right"
    }
    var text = `

        <div class="message-content" style="float: ${internalfloat};">
        <p class="${internalClass} custom-i">${message['message']}</p>
            <div class="message-footer" style="margin-top: 0px !important">${new Date(message['timestamp']).toLocaleString()}</div>
        </div>`



    
    let div = document.createElement("div");
    div.setAttribute("id", message['id']);
    if(message['messageType']==1)
    div.setAttribute("class", "message message-received message-first message-last message-tail");
    else
    div.setAttribute("class", "message message-sent message-first");
    div.innerHTML = text.trim();


    let p = document.createElement("p");
    p.setAttribute("id", message['id']);
    p.setAttribute("class", "custom-i");
    if(message['messageType']==1)
    p.setAttribute("class", "receive custom-i");
    else
    p.setAttribute("class", "send custom-i");
    p.innerHTML = message['message'];
    //return p
    return div

}


function showMessages(messageBox,number,name){
    updateRetrieveMessageBoxesInterval(2)
    messageBoxPage.hidden = true
    messagePage.hidden = false
    currentMessageBox = messageBox
    chatWindowName.innerHTML=name
    messagePage.setAttribute('data-number',number)
    messageSection.innerHTML=""

    getData('/api/sms/retrieve/port/'+port+'/messagebox/'+messageBox+'/messages').then(data =>{
        latestMessage = data[0]['id']
        oldestMessage = data[data.length-1]['id']
        for(message of data){
            div = messageParser(message)
            messageSection.prepend(div);
        }

        smsContent.scrollTop = smsContent.scrollHeight;
        updateMessagesIntervalID = setInterval(updateMessages,5000,messageBox);
    })
    
}

function updateMessages(messageBox){
    getData(`/api/sms/retrieve/port/${port}/messagebox/${messageBox}/messages/2/${latestMessage}`).then(data =>{
        if(data.length>0){
            latestMessage = data[0]['id']
            data = data.reverse()
            for(message of data){
                div = messageParser(message)
                messageSection.append(div);

            }
        }
    })
}

function getOlderMessages(){
    console.log("getting older messages")
    getData(`/api/sms/retrieve/port/${port}/messagebox/${currentMessageBox}/messages/1/${oldestMessage}`).then(data =>{
        if(data.length>0){
            oldestMessage = data[data.length-1]['id']
            for(message of data){
                div = messageParser(message)
                messageSection.prepend(div);

            }
        }
        getOlderMessagesInProcess = false
    })
}

function showMessageBoxes(){
    console.log(currentMessageBox)
    clearInterval(updateMessagesIntervalID)
    updateRetrieveMessageBoxes()
    updateRetrieveMessageBoxesInterval(1)
    messageBoxPage.hidden = false
    messagePage.hidden = true
    document.getElementById(`read-${currentMessageBox}`).classList.remove('avatar-online')
}

sendSMS.addEventListener("submit", function(e){
    e.preventDefault()
    var dataset = {
        "number": messagePage.dataset.number,
        "message":textMessageInput.value
    };
    postData(`/api/sms/send/port/${port}`,dataset).then(data=>{
        updateMessages(currentMessageBox)
        smsContent.scrollTop = smsContent.scrollHeight;
        textMessageInput.value=""  
    }
    )
})
var getOlderMessagesInProcess = false
smsContent.addEventListener('scroll', function(e) {
    console.log('working i guess')
    var {
        scrollTop,
        scrollHeight,
        clientHeight
    } = smsContent;
    if(scrollTop<10 && getOlderMessagesInProcess==false){
        getOlderMessagesInProcess=true
        getOlderMessages()
    }
});


chatBoxContent.addEventListener('scroll', function(e) {
    console.log('working chat')
    var {
        scrollTop,
        scrollHeight,
        clientHeight
    } = chatBoxContent;
    var factor = scrollHeight-(clientHeight+scrollTop);
    console.log(factor)
    
    if(factor<1 && oldRetrieveMessageBoxesInProcess==false){
        oldRetrieveMessageBoxesInProcess = true
        oldRetrieveMessageBoxes()
        
        
    }
});
retrieveMessageBoxes()