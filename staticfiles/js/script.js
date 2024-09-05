document.getElementById('logout-btn').addEventListener('click', function() {
    document.getElementById('logout-dialog').showModal();
});

document.getElementById('close-dialog').addEventListener('click', function() {
    document.getElementById('logout-dialog').close();
});

document.getElementById('cancel-logout').addEventListener('click', function() {
    document.getElementById('logout-dialog').close();
});

// document.getElementById('confirm-logout').addEventListener('click', function() {
//     window.location.href = "{% url 'logout' %}";
// });
document.getElementById('logout-confirm-btn').addEventListener('click', function() {
    window.location.href = "{% url 'logout' %}";
});
