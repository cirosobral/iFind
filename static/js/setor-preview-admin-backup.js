
var pin = document.querySelectorAll(".item");

var container_pinos = document.querySelector("#pinos");
var activeItem = null;

var active = false;

container_pinos.addEventListener("touchstart", dragStart, false);
container_pinos.addEventListener("touchend", dragEnd, false);
container_pinos.addEventListener("touchmove", drag, false);

container_pinos.addEventListener("mousedown", dragStart, false);
container_pinos.addEventListener("mouseup", dragEnd, false);
container_pinos.addEventListener("mousemove", drag, false);

let position = [];

let savePosition;
let loadPosition;


// Requisitando posições
let requisicao = fetch('save-data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(''),
}).then(response => {
    return response.json();
}).then(data => {
    // salvando as posições no LocalStorage
    for (var i = 0; i < data.length; i++) {
        localStorage.setItem(`position${i}`, JSON.stringify(data[i]));
        console.log(localStorage)
    }
});


for (var i = 0; i < pin.length; i++) {
    loadPosition = () => {
        position[i] = JSON.parse(localStorage.getItem(`position${i}`));
        if (position[i]) {
            pin[i].style.top = `${position[i].y}px`;
            pin[i].style.left = `${position[i].x}px`;
        }
        console.log("loadPosition = ", position[i]);
    };

    loadPosition();
}

function dragStart(e) {

    if (e.target !== e.currentTarget) {
        active = true;

        // this is the item we are interacting with
        activeItem = e.target;

        if (activeItem !== null) {
            if (!activeItem.xOffset) {
                activeItem.xOffset = 0;
            }

            if (!activeItem.yOffset) {
                activeItem.yOffset = 0;
            }

            if (e.type === "touchstart") {
                activeItem.initialX = e.touches[0].clientX - activeItem.xOffset;
                activeItem.initialY = e.touches[0].clientY - activeItem.yOffset;
            } else {
                console.log("doing something!");
                activeItem.initialX = e.clientX - activeItem.xOffset;
                activeItem.initialY = e.clientY - activeItem.yOffset;
            }
        }
    }
}

function dragEnd(e) {
    if (activeItem !== null) {
        activeItem.initialX = activeItem.currentX;
        activeItem.initialY = activeItem.currentY;
    }

    active = false;
    activeItem = null;

    for (var i = 0; i < pin.length; i++) {
        savePosition = () => {
            position[i] = { x: pin[i].getBoundingClientRect().x, y: pin[i].getBoundingClientRect().y };
            localStorage.setItem(`position${i}`, JSON.stringify(position[i]));
            console.log("savePosition = ", position[i]);
        };
        savePosition();

    }

    /*
    fetch(position, {
        method: 'POST',
        body: JSON.stringify({ x: 10, y: 20 }),
        header: { 'content-type': 'application/json' }
    });
    */

}

function drag(e) {
    if (active) {
        if (e.type === "touchmove") {
            e.preventDefault();

            activeItem.currentX = e.touches[0].clientX - activeItem.initialX;
            activeItem.currentY = e.touches[0].clientY - activeItem.initialY;
        } else {
            activeItem.currentX = e.clientX - activeItem.initialX;
            activeItem.currentY = e.clientY - activeItem.initialY;
        }

        activeItem.xOffset = activeItem.currentX;
        activeItem.yOffset = activeItem.currentY;

        setTranslate(activeItem.currentX, activeItem.currentY, activeItem);
    }
}

function setTranslate(xPos, yPos, el) {
    el.style.transform = "translate3d(" + xPos + "px, " + yPos + "px, 0)";
}

function createPino() {
    var pino = document.createElement("div");
    pino.setAttribute("class", "item");
    container_pinos.appendChild(pino);
}

function deletePino() {
    var last_pino = document.querySelector("div .item");
    last_pino.remove();
}