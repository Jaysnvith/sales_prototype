$(document).ready(function() {
    $('#mastertable').DataTable({
        responsive: true,
        columnDefs: [
            { orderable: false, targets: 'disable-sorting' }
        ],
    });
});
