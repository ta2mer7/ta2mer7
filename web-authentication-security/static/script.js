function checkPasswordStrength(password) {
    let strength = "Weak";
    let color = "red";

    if (password.length > 8) {
        strength = "Medium";
        color = "orange";
    }

    if (/[A-Z]/.test(password) && /[0-9]/.test(password)) {
        strength = "Strong";
        color = "lime";
    }

    const el = document.getElementById("strength");

    if (el) {
        el.innerText = strength;
        el.style.color = color;
    }
}

window.addEventListener("load", () => {
    document.getElementById("loader").style.display = "none";
});

function loadStats(){
    fetch('/api/stats')
    .then(res => res.json())
    .then(data => {

        document.getElementById("users").innerText = data.users;
        document.getElementById("success").innerText = data.success;
        document.getElementById("failed").innerText = data.failed;

        // 🚨 ALERT إذا في هجمات
        if(data.failed > 5){
            showAlert("⚠️ Possible attack detected!");
        }

    });
}

// تحديث كل 3 ثواني
setInterval(loadStats, 3000);

// أول تحميل
loadStats();

function showAlert(msg){
    let box = document.getElementById("alertBox");

    let alert = document.createElement("div");
    alert.className = "alert";
    alert.innerText = msg;

    box.appendChild(alert);

    setTimeout(()=>{
        alert.remove();
    }, 3000);
}

// =========================
// LOADER
// =========================

window.addEventListener("load", ()=>{

    const loader = document.getElementById("loader");

    loader.style.opacity = "0";

    setTimeout(()=>{
        loader.style.display = "none";
    },500);

});

// =========================
// TERMINAL ANIMATION
// =========================

const terminal = document.getElementById("terminal");

if(terminal){

const lines = [

"[OK] Firewall Enabled",
"[OK] Database Connected",
"[INFO] Monitoring Traffic...",
"[OK] Secure Authentication Active",
"[WARNING] Suspicious login blocked",
"[INFO] Live Protection Enabled",
"[OK] AI Threat Detection Running",
"[OK] Encryption Active"

];

let i = 0;

function addLine(){

    if(i < lines.length){

        let div = document.createElement("div");

        div.innerText = lines[i];

        terminal.appendChild(div);

        i++;

    }else{

        terminal.innerHTML = "";
        i = 0;

    }

}

setInterval(addLine,1200);

}

// ================= MATRIX =================

const canvas = document.getElementById("matrix");

if(canvas){

const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const letters = "01";
const fontSize = 14;

const columns = canvas.width / fontSize;

const drops = [];

for(let x=0;x<columns;x++){
    drops[x]=1;
}

function drawMatrix(){

    ctx.fillStyle = "rgba(0,0,0,0.05)";
    ctx.fillRect(0,0,canvas.width,canvas.height);

    ctx.fillStyle="#00e5ff";
    ctx.font = fontSize + "px monospace";

    for(let i=0;i<drops.length;i++){

        const text = letters[Math.floor(Math.random()*letters.length)];

        ctx.fillText(text,i*fontSize,drops[i]*fontSize);

        if(drops[i]*fontSize > canvas.height && Math.random() > 0.975){
            drops[i]=0;
        }

        drops[i]++;
    }

}

setInterval(drawMatrix,35);

}

// ================= LIVE NUMBERS =================

function animateValue(id,start,end,duration){

let obj = document.getElementById(id);

if(!obj) return;

let range = end-start;

let current = start;

let increment = end > start ? 1 : -1;

let stepTime = Math.abs(Math.floor(duration/range));

let timer = setInterval(()=>{

    current += increment;

    obj.innerText = current;

    if(current == end){
        clearInterval(timer);
    }

},stepTime);

}

animateValue("attacks",0,1287,3000);
animateValue("usersLive",0,524,3000);
animateValue("threats",0,93,3000);