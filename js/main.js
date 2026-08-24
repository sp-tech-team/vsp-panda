(() => {
    const doc = window.parent.document;

    if (doc.__submitLockListenerInstalled) {
        return;
    }

    doc.__submitLockListenerInstalled = true;

    doc.addEventListener(
        "click",
        function (event) {

            const button = event.target.closest("button");

            if (!button) {
                return;
            }

            // Find the Streamlit element corresponding
            // to key="submit"
            const container = button.closest(
                '[class*="st-key-submit"]'
            );

            if (!container) {
                return;
            }

            console.log("Submit Request pressed");

            // Disable immediately
            // doc.querySelectorAll(
            //     'input, select, textarea, button'
            // ).forEach(function (element) {
            //     element.disabled = true;
            // });
            button.disabled = true;

        },
        true
    );

    console.log("Submit lock listener installed");
})();