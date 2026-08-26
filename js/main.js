(() => {
    const doc = window.parent.document;

    if (doc.__submitLockListenerInstalled) {
        return;
    }

    doc.__submitLockListenerInstalled = true;

    doc.addEventListener("click", function (event) {

        const button = event.target.closest("button");

        if (!button) {
            return;
        }

        const container = button.closest('[class*="st-key-submit"]');

        if (!container) {
            return;
        }

        setTimeout(() => {
            button.disabled = true;

            // Remove previous validation-failed marker
            const validationMarker = doc.querySelector(
                "#request-validation-failed"
            );

            if (validationMarker) {
                validationMarker.remove();
            }
        }, 0);

    }, false);

    // Watch for Streamlit rerenders
    const observer = new MutationObserver(() => {

        const validationFailed = doc.querySelector("#request-validation-failed");

        if (validationFailed) {

            const submitContainer = doc.querySelector(
                '[class*="st-key-submit"]'
            );

            if (submitContainer) {
                const submitButton = submitContainer.querySelector("button");

                if (submitButton) {
                    submitButton.disabled = false;
                    console.log("Submit button re-enabled.");
                }
            }
        }
    });

    observer.observe(doc.body, {
        childList: true,
        subtree: true
    });
})();