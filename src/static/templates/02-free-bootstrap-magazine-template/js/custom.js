jQuery(document).ready(function() {
    $("#current-date").html(function () {
        const current_date = new Date();
        date= current_date.getDate();
        day = current_date.toLocaleString('default', { weekday: 'long'});
        month=current_date.toLocaleString('default', { month: 'long'});
        year= current_date.getFullYear();
        return day + ', ' + month + ' ' + date + ' ' + year;
    });
});
