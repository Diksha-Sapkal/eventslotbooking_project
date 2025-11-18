// disable-past-dates for Django admin date popup (robust)
(function () {
    // Utility: zero time for Date
    function stripTime(d) {
        const t = new Date(d);
        t.setHours(0, 0, 0, 0);
        return t;
    }

    // Today's date (midnight)
    const today = stripTime(new Date());
    const minDateISO = today.toISOString().split("T")[0];

    // CSS class used for disabled cells - make sure your CSS file contains styling
    const DISABLED_CLASS = "disabled-day";

    // Add basic CSS fallback if not already present (optional)
    const addCSS = () => {
        if (document.getElementById("disable-past-dates-css")) return;
        const style = document.createElement("style");
        style.id = "disable-past-dates-css";
        style.textContent = `
.${DISABLED_CLASS} {
  pointer-events: none !important;
  opacity: 0.35 !important;
  background: #f5f5f5 !important;
  color: #999 !important;
  cursor: not-allowed !important;
}
`;
        document.head.appendChild(style);
    };

    addCSS();

    // Take a calendar element (the .calendarbox module) and disable past days inside it
    function disablePastDaysInCalendar(calendarbox) {
        try {
            if (!calendarbox) return;

            // Find the <table class="calendar"> inside the calendarbox
            const calTable = calendarbox.querySelector("table.calendar");
            if (!calTable) return;

            // The caption usually contains "MonthName Year" e.g. "November 2025"
            const caption = calTable.querySelector("caption");
            let captionText = caption ? caption.textContent.trim() : "";

            // Try to extract month name and year: fallback behaviour if caption is different
            // We'll attempt to match "MonthName 2025" or "2025 November" etc.
            const r1 = /([A-Za-z]+)\s+(\d{4})/.exec(captionText); // "November 2025"
            const r2 = /(\d{4})\s+([A-Za-z]+)/.exec(captionText); // "2025 November"
            let monthIndex = null;
            let year = null;

            if (r1) {
                const monthName = r1[1];
                year = parseInt(r1[2], 10);
                // parse monthName by creating a Date from 'monthName 1 year'
                const tmp = new Date(`${monthName} 1, ${year}`);
                if (!isNaN(tmp)) monthIndex = tmp.getMonth(); // 0-based
            } else if (r2) {
                const monthName = r2[2];
                year = parseInt(r2[1], 10);
                const tmp = new Date(`${monthName} 1, ${year}`);
                if (!isNaN(tmp)) monthIndex = tmp.getMonth();
            }

            // If we can't get month/year from caption, try to infer from currently selected input value
            if (monthIndex === null) {
                const activeInput = document.activeElement;
                if (activeInput && activeInput.classList.contains("vDateField") && activeInput.value) {
                    // input value is yyyy-mm-dd
                    const parts = activeInput.value.split("-");
                    if (parts.length === 3) {
                        year = parseInt(parts[0], 10);
                        monthIndex = parseInt(parts[1], 10) - 1;
                    }
                }
            }

            // If still missing, bail out (we don't want to produce wrong dates)
            if (monthIndex === null || !year) {
                // console.debug("disablePastDaysInCalendar: couldn't parse month/year", captionText);
                return;
            }

            // Query day cells
            const dayCells = calTable.querySelectorAll("td.day, td span"); // some themes may wrap day numbers
            if (!dayCells.length) return;

            dayCells.forEach(cell => {
                // cell.textContent should be the day number (1-31) or may contain whitespace
                const txt = cell.textContent.trim();
                const dayNumber = parseInt(txt, 10);
                if (!dayNumber || isNaN(dayNumber)) return;

                // Build date for this cell: year-monthIndex-dayNumber
                const cellDate = stripTime(new Date(year, monthIndex, dayNumber));

                if (cellDate < today) {
                    // mark disabled
                    cell.classList.add(DISABLED_CLASS);
                    // set aria-disabled & title for accessibility
                    cell.setAttribute("aria-disabled", "true");
                    if (!cell.getAttribute("title")) {
                        cell.setAttribute("title", "Past dates are disabled");
                    }
                } else {
                    // Ensure future days are not accidentally marked disabled (when navigating)
                    cell.classList.remove(DISABLED_CLASS);
                    cell.removeAttribute("aria-disabled");
                    if (cell.getAttribute("title") === "Past dates are disabled") {
                        cell.removeAttribute("title");
                    }
                }
            });
        } catch (err) {
            // Silently fail but log for debugging
            console.error("disablePastDaysInCalendar error:", err);
        }
    }

    // Called when a calendar node appears or updates
    function handleCalendarNode(calendarbox) {
        disablePastDaysInCalendar(calendarbox);

        // Add a click listener to the calendarbox so when user navigates months (prev/next),
        // we re-run the disabling logic after Django redraws the table.
        calendarbox.addEventListener("click", function (ev) {
            // small delay to allow calendar to update
            setTimeout(() => disablePastDaysInCalendar(calendarbox), 60);
        }, { capture: true, passive: true });
    }

    // Observe the document for added calendarbox nodes (Django injects popup)
    const observer = new MutationObserver(mutations => {
        for (const m of mutations) {
            if (!m.addedNodes || !m.addedNodes.length) continue;
            m.addedNodes.forEach(node => {
                if (!(node instanceof Element)) return;
                // direct calendarbox div insertion
                if (node.matches && node.matches(".calendarbox, .calendarbox.module")) {
                    handleCalendarNode(node);
                }
                // or calendar nested somewhere under node
                const boxes = node.querySelectorAll ? node.querySelectorAll(".calendarbox, .calendarbox.module") : [];
                boxes.forEach(box => handleCalendarNode(box));
            });
        }
    });

    // Start observing
    observer.observe(document.documentElement || document.body, {
        childList: true,
        subtree: true
    });

    // Also attach to existing calendarboxes already in DOM (if any)
    document.querySelectorAll(".calendarbox, .calendarbox.module").forEach(cb => handleCalendarNode(cb));

    // Apply min attribute to inputs, validate on change and on form submit
    function initDateInputs() {
        const inputs = document.querySelectorAll("input.vDateField[type=date], input.vDateField");
        inputs.forEach(input => {
            try {
                // set HTML5 min attribute (prevents browsers that honor it)
                input.setAttribute("min", minDateISO);

                // On change, enforce min
                input.addEventListener("change", function (ev) {
                    const val = input.value;
                    if (!val) return;
                    // value expected in ISO yyyy-mm-dd
                    if (val < minDateISO) {
                        input.value = minDateISO;
                        // small feedback
                        if (window.alert) {
                            // use a non-blocking visual clue if desired; alert kept for compatibility
                            // Comment out alert if you don't want popups
                            alert("Past dates are disabled. Date set to today.");
                        }
                    }
                });
            } catch (e) { /* ignore per input errors */ }
        });
    }

    // initial setup
    document.addEventListener("DOMContentLoaded", function () {
        initDateInputs();

        // If admin loads extra fields after DOM ready, also initialize them (delegate)
        document.body.addEventListener("focusin", function (ev) {
            const el = ev.target;
            if (el && el.classList && el.classList.contains("vDateField")) {
                // small timeout to let calendar open
                setTimeout(() => initDateInputs(), 20);
            }
        });
    });

    // For debugging: expose helper on window (only if needed)
    window.__disablePastDatesForAdmin = {
        disablePastDaysInCalendar,
        minDateISO,
        today: today.toISOString()
    };
})();
