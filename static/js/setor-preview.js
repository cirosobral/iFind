localStorage.clear();

var pin = document.querySelectorAll(".item");

let positionStringify = [];
let position = [];

let loadPosition;

// Requisitando posições
let requisicaoLoad = fetch('/load-data').then(response => {
    if (response.ok) {
        console.log('Sucesso ao receber dados')
        return response.json();
    }
    throw new Error('Erro ao receber dados')
}).then(data => {
    // salvando as posições no LocalStorage
    for (var i = 0; i < data.length; i++) {
        //localStorage.setItem(`position${i}`, JSON.stringify(data[i]));
        //console.log(localStorage)
        positionStringify[i] = JSON.stringify(data[i]);
        position[i] = JSON.parse(positionStringify[i]);

        console.log(position[i])
        if (position[i]) {
            pin[i].style.top = `${position[i].y}px`;
            pin[i].style.left = `${position[i].x}px`;
        }
    }
    //console.log(localStorage)

    /*
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
    */
});