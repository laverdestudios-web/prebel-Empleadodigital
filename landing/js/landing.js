const panel = document.getElementById('chatPanel');
const launch = document.getElementById('chatLaunch');
const close = document.getElementById('chatClose');
function setChat(open){
  panel.classList.toggle('open', open);
  launch.setAttribute('aria-expanded', String(open));
}
launch.addEventListener('click', () => setChat(!panel.classList.contains('open')));
close.addEventListener('click', () => setChat(false));
document.querySelectorAll('[data-open-chat]').forEach(button => button.addEventListener('click', () => setChat(true)));
document.querySelectorAll('[data-topic]').forEach(button => button.addEventListener('click', () => {
  const status = document.getElementById('chatStatus');
  status.textContent = 'Tema seleccionado: ' + button.dataset.topic + '. La conexión con el chatbot debe configurarse para recibir y responder esta consulta.';
  document.querySelector('.chat-body .bubble').textContent = 'Has seleccionado: ' + button.dataset.topic + '. Cuando se conecte el chatbot institucional, aquí podrás continuar tu consulta.';
}));
document.getElementById('year').textContent = new Date().getFullYear();
