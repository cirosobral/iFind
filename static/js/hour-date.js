
function atualizar() {
    const meses = [
        'Janeiro',
        'Fevereiro',
        'Março',
        'Abril',
        'Maio',
        'Junho',
        'Julho',
        'Agosto',
        'Setembro',
        'Outubro',
        'Novembro',
        'Dezembro'
    ];

    const agora = new Date();
    const ano = agora.getFullYear();
    const mes = agora.getMonth();
    const dia = agora.getDate();

    // const hora = agora.getHours();
    // const minuto = agora.getMinutes();
    // const segundo = agora.getSeconds();

    let month = meses[mes];


    var hour = document.getElementById("bar-hour");
    var date = document.getElementById("bar-date");

    // if (hora < 10) {
    //     let hr = '0' + hora
    //     if (minuto < 10) {
    //         let min = '0' + minuto
    //         hour.innerHTML = hr + ':' + min + ':' + segundo;
    //     } else {
    //         hour.innerHTML = hr + ':' + minuto + ':' + segundo;
    //     }

    // } else {
    //     if (minuto < 10) {
    //         let min = '0' + minuto
    //         hour.innerHTML = hora + ':' + min + ':' + segundo;
    //     } else {
    //         hour.innerHTML = hora + ':' + minuto + ':' + segundo;
    //     }
    // }

    // Não parei para analisar o motivo, mas, eventualmente, minutos e segundos estavam sendo apresentados com apenas um dígito.
    // O método toLocalTimeString faz as correções que vocês buscaram implementar acima.
    hour.innerText = agora.toLocaleTimeString();

    date.innerHTML = dia + ' de ' + month.toString() + ', ' + ano;

}

setInterval(atualizar, 1000);
