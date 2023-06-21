const pinos = document.querySelectorAll(".item")
const container_pinos = document.querySelector("#pinos")

const moverPino = (evt) => {
    // Evita o scroll quando estiver carregando o pino
    evt.preventDefault()

    // Busca o elemento que está sendo movido
    let el = evt.currentTarget.currentElement

    // Calcula o deslocamento
    let deslocamento = calcularDeslocamento(container_pinos,
        (evt.constructor.name == 'TouchEvent' ? evt.changedTouches[0] : evt))

    // Realiza o deslocamento
    deslocarPino(el, deslocamento)
}

const salvarPino = (evt) => {
    // Busca o elemento a ser salvo
    let el = evt.currentTarget.currentElement

    // Realiza o envio ao servidor
    fetch(`/save-data/${el.dataset['id']}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            x: el.style.left,
            y: el.style.top,
        })
    }).then(response => {
        if (response.ok) {
            console.log('Dados enviados com sucesso');
            return response.json();
        }
        throw new Error('Erro ao enviar dados');
    }).then(data => {
        console.log(data);
    });

    // Remove os eventlisteners no container
    container_pinos.removeEventListener('drag', moverPino)
    container_pinos.removeEventListener('drop', salvarPino)
    container_pinos.removeEventListener('touchmove', moverPino)
    container_pinos.removeEventListener('touchend', salvarPino)
}

const calcularDeslocamento = (container, evt) => {
    let origemContainer = {
        x: container.getBoundingClientRect().x,
        y: container.getBoundingClientRect().y,
    }

    return {
        x: `${(evt.clientX - origemContainer.x) / container.clientWidth * 100}%`,
        y: `${(evt.clientY - origemContainer.y) / container.clientHeight * 100}%`,
    }
}

const deslocarPino = (pino, deslocamento) => {
    pino.style.left = deslocamento.x
    pino.style.top = deslocamento.y
}

// Necessário para funcionar o evento de drop
container_pinos.addEventListener("dragover", (evt) => {
    evt.preventDefault()
})

// Define os eventlisteners para cada pino
pinos.forEach((el) => {
    // Adiciona o eventlistener para o caso do drag (carregar com o mouse)
    el.addEventListener("dragstart", (evt) => {
        // Oculta a imagem fantasma ao arrastar
        evt.dataTransfer.setDragImage(document.createElement('span'), 0, 0)

        // Define o elemento a ser alterado
        container_pinos.currentElement = el

        // Adiciona os eventlisteners ao container
        container_pinos.addEventListener('drag', moverPino)
        container_pinos.addEventListener('drop', salvarPino)
    })

    // Adiciona o eventlistener para o início do toque (carregar com o touch)
    el.addEventListener("touchstart", (evt) => {
        // Define o elemento a ser alterado
        container_pinos.currentElement = el

        // Adiciona os eventlisteners ao container
        container_pinos.addEventListener('touchmove', moverPino)
        container_pinos.addEventListener('touchend', salvarPino)
    })
})