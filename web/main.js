//這邊必須要async funciton 因為python返回需要時間，而JS 又不會block，
//所以需要用async function 加上await去呼叫PY function
let register_button = document.getElementById("register_button");
let register_name_button = document.getElementById("register_name");
let nodeList        = document.getElementById("node-list");
let bodynode        = document.getElementById("body-node")
let logonode        = document.getElementById("logo")
let reg_button      = document.getElementById("register")
//let need_water_sig = document.getElementsByClassName("need-water")[0]
let node_record = [];
let current_IP  = 0;
let current_name = 0;
let current_value = 0;
let current_cycle = 0;
let record_time = 0;
let record_value  = 0;
let main_child = 0;
let current_predict = 0;
let current_highbound = 0;
let current_need_water = 0;
let current_volume = 0;
let current_auto = "none"
let name_IP_map = {}
let IP_name_map = {}
let current_auto_input = 1

console.log(window.innerHeight, window.innerWidth)
console.log(bodynode.offsetWidth, bodynode.offsetHeight)


function get_auto(){
    let auto_node = document.getElementById('auto-input')
    current_volume = auto_node.value
}
function get_IP(e){
    current_IP = e.value
}

function get_name(e){
    current_name = e.value
}

function get_volume(){
    let volume_node = document.getElementById("watering-volume")
    console.log("fuck")
    console.log(volume_node.value)
    current_volume = volume_node.value
}

function get_cycle(){
    let cycle_node = document.getElementById("cycle-input")
    current_cycle = cycle_node.value*60*60
}

async function watering(IP, volume){
    await eel.watering(IP, volume)
}


function sig_color(water_node){
    console.log(current_value)
    console.log(current_need_water)
    if(current_need_water === "1"){
        water_node.style.background = "red"
    }
    else if(current_need_water === "0"){
        water_node.style.background = "green"
    }
}

function auto_color(){
    let auto_node = document.getElementById("auto-button")
    if(current_auto === "1"){
        auto_node.style.background = "red"
        auto_node.innerHTML = "close auto"
    }
    else if(current_auto === "0"){
        auto_node.style.background = "green"
        auto_node.innerHTML = "open auto"
    }
}
async function connect(IP){
    //呼叫的方式，就是加上eel.加上剛剛被expose PY function的名稱然後多加()輸入參數，最後加()取值
    await eel.connect(IP)()  
    
    //最後將返回的值設定在HTML上的<p>內
    //document.querySelector('p').textContent = result
}

function insert_node(name, IP){
    ip_node = document.createElement("div")
    ip_node.setAttribute('class', 'ip-button')
    name_IP_map[name] = IP
    IP_name_map[IP] = name
    ip_node.addEventListener('click', function(){
        connect(IP);
        set_node(IP);
    });
    ip_node.innerHTML = name
    nodeList.appendChild(ip_node)
}

function insert_nodes(){
    nodeList.innerHTML = ''
    for(var i=0; i<node_record.length; ++i)
    {
        stm_name = node_record[i].split(" ")[0]
        ip = node_record[i].split(" ")[1] + " " + node_record[i].split(" ")[2]
        insert_node(stm_name, ip)
    }
}

async function set_cycle(IP, cycle){
    await eel.set_cycle(IP, cycle)
}
function set_node(IP){
    current_IP = IP
    body_to_node()
}
async function get_nodes(){
    result = await eel.get_nodes()()
    node_record = result
    console.log(node_record)
    insert_nodes()
    return result
}

async function predict(IP){
    result = await eel.predict(IP)()
    return result
}

async function sethighbound(IP){
    await eel.sethighbound(IP)()
    await refresh()
    
}

async function last_interval(IP){
    result = await eel.last_interval(IP)()
    return result
}
async function exit(){
    await exit()()
}

async function register(name,IP){
    await eel.register(name,IP)
}


async function transfer(IP){
    result = await eel.transfer(IP)()
    current_value = result[0]
    current_need_water = result[1]
}

async function getsequence(IP){
    result = await eel.getsequence(IP)()
    return result
}

async function reset(){
    register_button = 0
    nodeList = 0
}

async function ask_auto(IP){
    result = await eel.ask_auto(IP)()
    console.log(result)
    current_auto = result
}

async function set_auto(IP,volume){
    console.log("set auto")
    await eel.auto_watering(IP,volume)()
}

async function set_anti_auto(IP){
    await eel.anti_auto_watering(IP)()
}

async function refresh(){
    await body_to_node()
}

async function node_to_body(){
    bodynode.innerHTML = ''
    b1_node =document.createElement("DIV")
    b1_node.setAttribute("class","b1")
    hello_node = document.createElement("DIV")
    hello_node.setAttribute("class","top-banner")
    logo_node = logonode
    hello_node.appendChild(logo_node)
    b1_node.appendChild(hello_node)
    register_node = document.createElement("DIV")
    register_node.setAttribute("class","register-part")
    register_but_node = document.createElement("DIV")
    register_but_node.setAttribute("class","register_button_part")
    label_node = reg_button
    input_node = register_button
    /*input_node = document.createElement("INPUT")
    input_node.setAttribute("id","register_button")
    input_node.setAttribute("name","register_button")
    input_node.setAttribute("type","text")
    input_node.setAttribute("placeholder","What need to be done?")*/
    register_but_node.appendChild(label_node)
    register_but_node.appendChild(input_node)
    register_but_node.appendChild(register_name_button)
    register_node.appendChild(register_but_node)
    b1_node.appendChild(register_node)
    ip_list_node = document.createElement("DIV")
    ip_list_node.setAttribute("class","ip-list")
    ip_node = nodeList
    /*ip_node = document.createElement("DIV")
    ip_node.setAttribute("id","node-list")*/
    ip_list_node.appendChild(ip_node)
    b1_node.appendChild(ip_list_node)
    /*script_node = document.createElement("SCRIPT")*/
    /*script_node.setAttribute("type","text/javascript")*/
    /*script_node.setAttribute("src","./main.js")*/
    bodynode.appendChild(b1_node)
    /*bodynode.appendChild(script_node)*/
    insert_nodes()

}
async function body_to_node(){
    console.log("current IP: "+current_IP)
    bodynode.innerHTML = ''
    b2_node = document.createElement("DIV")
    b2_node.setAttribute("class","b2")  //----

    div_info_node = document.createElement("DIV")
    div_info_node.setAttribute("class","info-part") //----

    div_control_node = document.createElement("DIV")
    div_control_node.setAttribute("class","control-part") //----
    sethighbound_node = document.createElement("BUTTON")
    sethighbound_node.innerHTML = "set high bound"
    sethighbound_node.addEventListener('click',async function(){
        current_highbound = await sethighbound(current_IP)
    })
    div_data_node = document.createElement("DIV")
    div_data_node.setAttribute("class", "data")

    
    console.log(current_IP)
    await transfer(current_IP)
    console.log(current_value)
    current_value = current_value.replace("(","")
    current_value = current_value.replace(")","")
    current_value = current_value.split(",")
    record_time = String(current_value[0])
    record_value = String(current_value[1])

    ip_node = document.createElement("SPAN")
    ip_node.setAttribute("id", "ip-node")
    ip_node.innerHTML = "Current IP: " + current_IP
    value_node = document.createElement("SPAN")
    value_node.setAttribute("id", "value-node")
    value_node.innerHTML = "Current Value: " + record_value
    time_node = document.createElement("SPAN")
    time_node.setAttribute("id", "time-node")
    time_node.innerHTML = "Record Time: " + record_time
    //predict_time_node = document.createElement('SPAN')
    //predict_time_node.setAttribute("id", "predict-node")
    //predict_time_node.innerHTML =  "predict time: " + await predict(current_IP)
    interval_node = document.createElement('SPAN')
    interval_node.setAttribute("id","interval")
    last_record_node = document.createElement('SPAN')
    last_record_node.setAttribute("id","last-record")
    last_data = await last_interval(current_IP)
    console.log(last_data)
    interval_node.innerHTML = "last duration: " + last_data[0]
    last_record_node.innerHTML = "last record: " + last_data[1]
    await ask_auto(current_IP)
    await getsequence(current_IP)
    div_img_node = document.createElement("DIV") 
    div_img_node.setAttribute("class","data-img") //----
    img_node = document.createElement("IMG")
    img_node.setAttribute("src", "sequence.png") //----




    refresh_node = document.createElement("BUTTON")
    refresh_node.innerHTML = "refresh"
    refresh_node.addEventListener("click", async function(){
        await refresh()
    })
    water_node = document.createElement("DIV")
    water_node.setAttribute("class","need-water")
    water_node.setAttribute("id","need-water")
    watering_info_node = document.createElement("DIV")
    watering_node = document.createElement("BUTTON")
    watering_node.setAttribute("id","watering-button")
    watering_node.innerHTML = "watering"
    watering_volume_node = document.createElement("INPUT")
    watering_volume_node.setAttribute("placeholder","1~9")
    watering_volume_node.setAttribute("id","watering-volume")
    watering_volume_node.onchange = function(){get_volume()}
    watering_info_node.appendChild(watering_node)
    cycle_node = document.createElement('DIV')
    cycle_node.setAttribute("id","cycle-div")
    cycle_button_node = document.createElement('BUTTON')
    cycle_button_node.setAttribute("id","cycle-button")
    cycle_button_node.innerHTML = "set cycle"
    cycle_input_node = document.createElement('INPUT')
    cycle_input_node.setAttribute("id","cycle-input")
    cycle_input_node.setAttribute("placeholder", "1~24")
    cycle_input_node.onchange = function(){get_cycle()}
    cycle_button_node.addEventListener("click", async function(){
        await set_cycle(current_IP, current_cycle)
        current_cycle = 0
        let cyclenode = document.getElementById("cycle-input")
        cyclenode.value = ""
    })
    cycle_node.appendChild(cycle_button_node)
    cycle_node.appendChild(cycle_input_node)
    div_control_node.appendChild(water_node)
    watering_info_node.appendChild(watering_volume_node)
    div_control_node.appendChild(watering_info_node)
    div_control_node.appendChild(cycle_node)
    div_control_node.appendChild(sethighbound_node)
    div_control_node.appendChild(refresh_node)
    watering_node.addEventListener("click",async function(){
        console.log(current_volume)
        await watering(current_IP, current_volume)
        let volume_node = document.getElementById("watering-volume")
        volume_node.value = ""
        current_value = ""
    })
    sig_color(water_node)
    back_node = document.createElement("BUTTON")
    back_node.innerHTML = "back to home"
    back_node.addEventListener('click',function(){
        node_to_body()
    });
    auto_div_node = document.createElement('DIV')
    auto_node = document.createElement('BUTTON')
    auto_node.setAttribute("id","auto-button")
    auto_node.addEventListener("click", async function(){
        if(current_auto === "1"){
            await set_anti_auto(current_IP)
            current_auto = "0"
        }
        else if(current_auto === "0"){
            console.log("entering")
            await set_auto(current_IP,current_volume)
            console.log(current_volume)
            current_auto = "1"
            current_volume = 1
            let input_node = document.getElementById('auto-input')
            input_node.value = ""

            console.log("entering finish")
        }
        else{
            console.log("auto error occurs")
        }
        auto_color()
    })
    auto_input_node = document.createElement('INPUT')
    auto_input_node.setAttribute("id","auto-input")
    auto_input_node.onchange = function(){get_auto()}
    auto_div_node.appendChild(auto_node)
    auto_div_node.appendChild(auto_input_node)
    div_control_node.appendChild(auto_div_node)
    div_control_node.appendChild(back_node)
    div_img_node.appendChild(img_node)
    //div_data_node.appendChild(ip_node)
    div_data_node.appendChild(value_node)
    div_data_node.appendChild(time_node)
    //div_data_node.appendChild(predict_time_node)
    div_data_node.appendChild(interval_node)
    div_data_node.appendChild(last_record_node)
    div_info_node.appendChild(div_img_node)
    div_info_node.appendChild(div_data_node)
    b2_node.appendChild(div_info_node)
    b2_node.appendChild(div_control_node)
    bodynode.appendChild(b2_node)
    auto_color()
}

function SetRegisterEvent(){
    reg_button.addEventListener('click', function(){
        register(current_name,current_IP)
        current_IP = ""
        current_name = ""
        register_button.value = ""
        register_name_button.value = ""
        get_nodes()
    }
    );
}








SetRegisterEvent()
get_nodes()






