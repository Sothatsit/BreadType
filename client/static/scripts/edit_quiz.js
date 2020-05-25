/**
 * This code makes users click the button to delete a quiz three times
 * before it will redirect them to actually delete the quiz.
 *
 * This is done to reduce the chances of someone unintentionally deleting a quiz.
 */


// Stores the state for the delete button.
var deleteState = {
    clickCount: 0
};

// Once the document has been loaded, setup our listeners.
$(document).ready(function() {
    // When the user clicks the delete button.
    $('#delete').click(function() {
        deleteState.clickCount += 1;

        if (deleteState.clickCount === 1) {
            $('#delete')[0].innerText = "Are you sure?";
        } else if (deleteState.clickCount === 2) {
            $('#delete')[0].innerText = "Confirm Delete";
        } else if (deleteState.clickCount > 2) {
            window.location.href = window.location.href.replace("/edit", "/delete");
        }
    });
});
