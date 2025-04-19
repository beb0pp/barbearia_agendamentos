// Exemplo de script para alertar agendamento
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', () => {
            alert("Agendamento realizado com sucesso!");
        });
    }
});
