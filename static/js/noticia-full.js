// Quebra de linha dos paragráfos
const texto = document.getElementById('texto');
texto.innerHTML = texto.innerHTML.replace(/\n/g, '<br>');

const br = document.getElementsByTagName('br');
br[0].remove()

// Adicionar imagem no meio do paragráfo.
const img = document.querySelector('.img');
const contentText = texto.textContent;
br[0].remove()
texto.insertBefore(img, texto.childNodes[8]);

