$(document).ready(function() {
    $('#mastertable').DataTable({
        responsive: true,
        keys: true,
        columnDefs: [
            { orderable: false, targets: 'disable-sorting' }
        ],
    });
});
