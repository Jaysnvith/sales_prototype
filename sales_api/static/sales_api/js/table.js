$(document).ready(function() {
    $('#mastertable').DataTable({
        keys: true,
        stateSave: true,
        columnDefs: [
            { orderable: false, targets: 'disable-sorting' }
        ],
    });
});
