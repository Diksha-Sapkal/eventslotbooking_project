document.addEventListener("DOMContentLoaded", function () {
    const today = new Date().toISOString().split("T")[0];

    // For start_date and end_date fields
    const dateFields = document.querySelectorAll("#id_start_date, #id_end_date");

    dateFields.forEach(field => {
        field.setAttribute("min", today);
    });
});
