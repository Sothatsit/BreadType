
console.log("quiz.js loaded");

function sliderValUpdate(name) {
    // Dynamically update the slider number to be equal to the value
    var id = `${name}_slider_val`;
    var sliderval = document.getElementById(id);
    var slider = document.getElementsByName(name);
    
    sliderval.innerHTML = slider[0].value;
}