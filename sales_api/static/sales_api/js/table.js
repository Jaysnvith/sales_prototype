$(document).ready(function() {
    $('#mastertable').DataTable({
        keys: true,
        stateSave: true,
        scrollX: true,
        columnDefs: [
            { orderable: false, targets: 'disable-sorting' }
        ],
    });
});
