document.addEventListener("DOMContentLoaded", function () {

    const deleteButtons =
        document.querySelectorAll(".delete-history");

    deleteButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const historyItem =
                button.closest(".history-item");

            if (confirm("Are you sure you want to delete this history item?")) {

                if (historyItem) {
                    historyItem.remove();
                }

            }

        });

    });

});