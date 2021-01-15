let current_value = 0;
let node_IP    = current_IP;

async function transfer(IP){
    result = await eel.transfer(IP)()
    current_value = result
}

async function getsequence(IP){
    result = await eel.getsequence(IP)()
    return result
}
async function get_current_value(){
    await transfer(node_IP)()
    value_node = document.getElementById("value node")
    value_node.innerHTML = current_value
}
console.log("node_IP")
console.log(node_IP)
get_current_value()