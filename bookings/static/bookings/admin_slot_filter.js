document.addEventListener("DOMContentLoaded", function () {
    const eventField = document.querySelector("#id_event");
    const slotField = document.querySelector("#id_slot");

    if (!eventField || !slotField) return;

    function loadSlots(eventId) {
        slotField.innerHTML = '<option value="">---------</option>';

        if (!eventId) return;

        fetch(`/admin/slots/slot/get_slots/?event_id=${eventId}`)
            .then(res => res.json())
            .then(data => {
                data.slots.forEach(slot => {
                    const opt = document.createElement("option");
                    opt.value = slot.id;
                    opt.textContent = slot.label;
                    slotField.appendChild(opt);
                });
            });
    }

    eventField.addEventListener("change", () => {
        loadSlots(eventField.value);
    });
});
