
// Once the document has been loaded, setup our listeners.
$(document).ready(function() {
    var questionNumber = 1;

    // Need at least one question.
    addQuestion(questionNumber);
    questionNumber += 1;

    // Setup the listener on the "Add Question" button to add more questions.
    $("#add_question").click(function() {
        addQuestion(questionNumber);
        questionNumber += 1;
    });
});


/**
 * Shorthand to create a div element with children
 */
function createDiv(className, children) {
    // Create the div.
    var div = document.createElement("div");
    div.className = className;

    // Add all of the children to the div.
    for(var index = 0; index < children.length; ++index) {
        div.appendChild(children[index]);
    }

    return div;
}


/**
 * Create a radio button element.
 */
function createRadioButton(radioName, text, onSelect, checked) {
    // The ID for this specific radio button, used to link the label and input elements.
    var formattedText = text.replace(" ", "_").toLowerCase();
    var inputID = `${radioName}_${formattedText}`;

    // Create the radio button itself.
    var input = document.createElement("input");
    input.type = "radio";
    input.checked = !!checked;
    input.value = text;
    input.name = radioName;
    input.id = inputID;
    input.onchange = () => { onSelect(text); };

    // Create the label associated with the radio button.
    var label = document.createElement("label");
    label.htmlFor = inputID;
    label.innerHTML = text;

    // Create a div to hold the input and label, and return it.
    return createDiv("choice", [input, label]);
}


/**
 * Create a check button element.
 */
function createCheckButton(checkName, text, checked) {
    // The ID for this specific check button, used to link the label and input elements.
    
    // A lot of repeating of radio button creater so feel free to combine to one
    // but tbh it works and i cant be bothered might do when i get it all working
    var formattedText = text.replace(" ", "_").toLowerCase();
    var inputID = `${checkName}_${formattedText}`;

    // Create the radio button itself.
    var input = document.createElement("input");
    input.type = "checkbox";
    input.checked = !!checked;
    input.value = text;
    input.name = `${checkName}_${formattedText}`;
    input.id = inputID;
    input.className = "bread_check";

    // Create the label associated with the check button.
    //var label = document.createElement("label");
    //label.htmlFor = inputID;
    //label.innerHTML = text;
    //label.style = "float:right"

    // Create a div to hold the input and label, and return it.
    return createDiv("choice", [input]);
}


/**
 * Create the div holding the inputs for the text of the question.
 */
function createQuestionTextEntryField(questionNumber) {
    // The name in the form for the text of this question.
    var questionTextFormName = `question_${questionNumber}_text`;

    // Create the label associated with the text field.
    var label = document.createElement("label");
    label.htmlFor = questionTextFormName;
    label.innerHTML = `Question ${questionNumber}`;

    // Create the text field itself.
    var input = document.createElement("input");
    input.type = "text";
    input.name = questionTextFormName;
    input.placeholder = "Enter your question here.";

    // Create a div to hold the input and label, and return it.
    return createDiv("question_text", [label, input])
}


/**
 * Called to add a new question to
 */
function addQuestion(questionNumber) {
    // Create the div to hold the question and its contents.
    var question = document.createElement("div");

    question.className = "question";
    question.id = `question_${questionNumber}`;

    // Create the input field and label for entering the question text.
    var questionTextDiv = createQuestionTextEntryField(questionNumber);
    question.appendChild(questionTextDiv);

    // Add the radio buttons for choosing the type of question.
    var questionTypeFormName = `question_${questionNumber}_type`;
    var onQuestionTypeChange = (text) => { changeType(questionNumber, text) };
    var questionTypeDiv = createDiv("question_type", [
        createRadioButton(questionTypeFormName, "Multiple Choice", onQuestionTypeChange, true),
        createRadioButton(questionTypeFormName, "Discrete Slider", onQuestionTypeChange),
        createRadioButton(questionTypeFormName, "Continuous Slider", onQuestionTypeChange)
    ]);
    question.appendChild(questionTypeDiv);

    // Append the div that will contain the configuration of the chosen question type.
    var questionConfigDiv = document.createElement("div");
    questionConfigDiv.id = `question_${questionNumber}_config`;
    question.appendChild(questionConfigDiv);

    // Add the question to the document.
    var questionBank = document.getElementById("question_bank");
    questionBank.appendChild(question);

    // Add a break to clear the floats of checkboxes
    var clearBreak = document.createElement("br");
    clearBreak.className = "clear";
    questionBank.appendChild(clearBreak);
    questionBank.appendChild(document.createElement("br"));

    // Setup the question to initially be a multiple choice question.
    changeType(questionNumber, "Multiple Choice");
}

/**
 * Sets up the document to allow configuration of the question based on its type.
 */
function changeType(questionNumber, type) {
    // Create the div to hold the configurations for the question type.
    var configDiv = document.createElement("div");
    configDiv.className = "question_config " + type.replace(" ", "_").toLowerCase();
    configDiv.id = `question_${questionNumber}_config`;

    // Setup the config div based on the type of question.
    if (type === "Multiple Choice") {
        setupMultiChoiceConfig(questionNumber, configDiv);
    } else if (type === "Discrete Slider") {
        setupDiscreteSliderConfig(questionNumber, configDiv);
    } else if (type === "Continuous Slider") {
        setupContinuousSliderConfig(questionNumber, configDiv);
    } else {
        throw new Error("Unknown question type \"" + type + "\"");
    }

    // Replace the config div with the newly created one.
    var questionDiv = document.getElementById(`question_${questionNumber}`);
    var oldConfigDiv = document.getElementById(`question_${questionNumber}_config`);
    questionDiv.replaceChild(configDiv, oldConfigDiv);
}


/**
 * Setup the config div for a multiple-choice question.
 */
function setupMultiChoiceConfig(questionNumber, configDiv) {
    // First find current bread names from boxes at top of page
    var checkboxLabels = document.getElementsByClassName("categories");

    for (var label_no = 0; label_no <4; ++label_no) {
        // The bread names are placed above the multi choice boxes
        var label = document.createElement("text")
        label.innerText = checkboxLabels[label_no].value;
        label.className = "check_label";
        configDiv.appendChild(label);
    }

    // Clears away the floating from checbox labels
    var clearBreak = document.createElement("br");
    clearBreak.className = "clear";
    configDiv.appendChild(clearBreak);

    for (var index = 1; index <= 4; ++index) {
        // The name in the form for this multi-choice option.
        var optionName = `question_${questionNumber}_multi_choice_${index}`;

        // The text field input for this option.
        var input = document.createElement("input");
        input.type = "text";
        input.name = optionName;
        input.className = "category";
        input.placeholder = `Multi-Choice Option ${index}`;

        // Another thing because stylesheet isn't overriding properly
        input.style = "width:80%; float:left";

        // Add in the checkboxes
        breadTypeFormName = `question_${questionNumber}_${index}`
        var breadTypeDiv = createDiv("bread_type", [
            createCheckButton(breadTypeFormName, checkboxLabels[0].value),
            createCheckButton(breadTypeFormName, checkboxLabels[1].value),
            createCheckButton(breadTypeFormName, checkboxLabels[2].value),
            createCheckButton(breadTypeFormName, checkboxLabels[3].value)
        ]);

        // Add the text field to the config div.
        configDiv.appendChild(input);
        configDiv.appendChild(breadTypeDiv);
    }
}


/**
 * Setup the config div for a discrete slider question.
 */
function setupDiscreteSliderConfig(questionNumber, configDiv) {
    setupSliderConfig(questionNumber, configDiv, true);
}


/**
 * Setup the config div for a continuous slider question.
 */
function setupContinuousSliderConfig(questionNumber, configDiv) {
    setupSliderConfig(questionNumber, configDiv, false);
}


/**
 * Setup the config div for a discrete or continuous slider question.
 */
function setupSliderConfig(questionNumber, configDiv, showStep) {
    // The name prefix for all of the slider parameters.
    var paramNamePrefix = `question_${questionNumber}_slider`;

    // Create the min/max inputs.
    var min = document.createElement("input");
    min.type = "number";
    min.min = "0";
    min.max = "10000";
    min.value = "0";
    min.name = paramNamePrefix + "_min";
    min.id = paramNamePrefix + "_min";
    var max = document.createElement("input");
    max.type = "number";
    max.min = "0";
    max.max = "10000";
    max.value = "100";
    max.name = paramNamePrefix + "_max";
    max.id = paramNamePrefix + "_max";

    // Create the labels associated with the inputs.
    var min_label = document.createElement("label");
    var max_label = document.createElement("label");
    min_label.htmlFor = paramNamePrefix + "_min";
    max_label.htmlFor = paramNamePrefix + "_max";
    min_label.innerHTML = "Enter the minimum value of the slider (0-10000)";
    max_label.innerHTML = "Enter the maximum value of the slider (0-10000)";

    // Add all the elements to the config div.
    configDiv.appendChild(min);
    configDiv.appendChild(min_label);
    configDiv.appendChild(document.createElement("br"));
    configDiv.appendChild(max);
    configDiv.appendChild(max_label);
    configDiv.appendChild(document.createElement("br"));

    if (showStep) {
        // Create the step input.
        var step = document.createElement("input");
        step.type = "number";
        step.min = "1";
        step.max = "1000";
        step.value = "1";
        step.name = paramNamePrefix + "_step";
        step.id = paramNamePrefix + "_step";

        // Create the associated label with the step input.
        var step_label = document.createElement("label");
        step_label.htmlFor = paramNamePrefix + "_step";
        step_label.innerHTML = "Enter the step of the slider (0-1000)";

        // Add all the elements for the step config.
        configDiv.appendChild(step);
        configDiv.appendChild(step_label);
        configDiv.appendChild(document.createElement("br"));
    }
}
