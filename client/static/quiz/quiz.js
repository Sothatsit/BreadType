
console.log("quiz.js loaded");

function addQuestion(qnum) {
    var textArea = document.getElementById("questionbank");
    var question = document.createElement("div");
    question.className = "question";
    question.name = `Question_${qnum}`;
    question.id = `Question_${qnum}`;
    question.appendChild(document.createTextNode(`Question ${qnum}`));

    var input = document.createElement("input");
    input.type = "text";
    input.name = `Question_${qnum}`
    input.placeholder = "Enter your question here."
    question.appendChild(input);

    var multi = document.createElement("input");
    multi.type = "radio";
    multi.checked = true;
    multi.onchange = function(){changeType(qnum, "multi")};
    multi.name = `radio_${qnum}`;
    question.appendChild(multi);
    
    var multi_label = document.createElement("label");
    multi_label.htmlFor = `Multi-Choice_${qnum}`;
    multi_label.innerHTML = "Multi-Choice&emsp;";
    multi_label.className = "radio_label";
    question.appendChild(multi_label);

    var int_slider = document.createElement("input");
    int_slider.type = "radio";
    int_slider.onchange = function(){changeType(qnum, "int_slider")};
    int_slider.name = `radio_${qnum}`;
    question.appendChild(int_slider);
    
    var int_slider_label = document.createElement("label");
    int_slider_label.htmlFor = `int_slider_${qnum}`;
    int_slider_label.innerHTML = "Integer Slider&emsp;";
    int_slider_label.className = "radio_label";
    question.appendChild(int_slider_label);

    var float_slider = document.createElement("input");
    float_slider.type = "radio";
    float_slider.onchange = function(){changeType(qnum, "float_slider")};
    float_slider.name = `radio_${qnum}`;
    question.appendChild(float_slider);
    
    var float_slider_label = document.createElement("label");
    float_slider_label.htmlFor = `float_slider_${qnum}`;
    float_slider_label.innerHTML = "Float Slider&emsp;";
    float_slider_label.className = "radio_label";
    question.appendChild(float_slider_label);

    question.appendChild(document.createElement("br"));
    question.appendChild(document.createElement("br"));
    question.appendChild(document.createElement("br"));
    question.appendChild(document.createElement("br"));

    textArea.appendChild(question);

    changeType(qnum, "multi");
}

function changeType(qnum, type) {
    var textArea = document.getElementById(`Question_${qnum}`);
    var options = document.createElement("div");
    options.className = type;
    options.name = `${type}_${qnum}`;
    
    if (type == "multi") {
        for(i=1;i<5;i++) {
            var option = document.createElement("input");
            option.name = `${type}_${qnum}_${i}`;
            option.type = "text";
            option.placeholder = `Multi-Choice Option ${i}`;
            options.appendChild(option);  
        }
    }
    
    else if (type.split("_")[1] == "slider") {
        var min = document.createElement("input");
        var max = document.createElement("input");
        min.type = "number";
        max.type = "number";
        min.min = 0;
        max.min = 0;
        min.max = 10000;
        max.max = 10000;
        min.placeholder = 0;
        max.placeholder = 100;
        min.name = `${type}_${qnum}_min`;
        max.name = `${type}_${qnum}_max`;
        var min_label = document.createElement("label");
        var max_label = document.createElement("label");
        min_label.htmlFor = `${type}_${qnum}_min`;
        max_label.htmlFor = `${type}_${qnum}_max`;
        min_label.innerHTML = "Enter the minimum value of the slider (0-10000)";
        max_label.innerHTML = "Enter the maximum value of the slider (0-10000)";
        options.appendChild(min);
        options.appendChild(min_label);
        options.appendChild(document.createElement("br"));
        options.appendChild(max);
        options.appendChild(max_label);
        options.appendChild(document.createElement("br"));
        if (type == "int_slider") {
            var step = document.createElement("input");
            step.type = "number";
            step.min = 1;
            step.max = 1000;
            step.placeholder = 1;
            step.name = `${type}_${qnum}_step`;
            var step_label = document.createElement("label");
            step_label.htmlFor = `${type}_${qnum}_step`;
            step_label.innerHTML = "Enter the step of the slider (0-1000)";
            options.appendChild(step);
            options.appendChild(step_label);
            options.appendChild(document.createElement("br"));
        }
    }
    
    textArea.replaceChild(options, textArea.childNodes[10]);
    console.log(`question ${qnum} was just changed`);
}