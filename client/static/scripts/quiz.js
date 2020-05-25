/**
 * This Javascript contains the code to dynamically update
 * the values shown below the sliders when their value is changed.
 */


/**
 * Updates the paragraph holding the value of the slider with the given name.
 */
function updateSliderValue(name) {
    // Find the elements we wish to update and retreive the value from.
    var sliderValueP = document.getElementById(`${name}_slider_val`);
    var slider = document.getElementsByName(name)[0];

    // Update the P tag holding the value of the slider.
    sliderValueP.innerText = slider.value;
}
