document.addEventListener("DOMContentLoaded", function () {
    const eventField = document.querySelector("#id_event");
    const slotField = document.querySelector("#id_slot");

    if (!eventField || !slotField) return;

    eventField.addEventListener("change", function () {
        const eventId = this.value;

        fetch(`/admin/slots/slot/get-slots/?event_id=${eventId}`)
            .then(res => res.json())
            .then(data => {
                slotField.innerHTML = "";
                data.slots.forEach(slot => {
                    const option = new Option(slot.label, slot.id);
                    slotField.appendChild(option);
                });
            });
    });
});
