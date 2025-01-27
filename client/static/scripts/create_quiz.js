/**
 * This file contains the code behind the create quiz page,
 * allowing users to dynamically add new questions to the form.
 */


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

    // Updates the category name labels when the category names change.
    var categoryInputs = $(".categories");
    categoryInputs.change(updateCategoryNames);
    categoryInputs.keyup(updateCategoryNames);
    categoryInputs.keydown(updateCategoryNames);
    categoryInputs.keypress(updateCategoryNames);

    // Stop the user pressing enter to create the quiz.
    $('form input').on('keypress', function(e) {
        return e.which !== 13;
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
function createCheckButton(checkName) {
    // Create the check button itself.
    var input = document.createElement("input");
    input.type = "checkbox";
    input.value = "Yes";
    input.name = checkName;
    input.className = "bread_check";
    return input;
}

function createNumberBoxes(numberName) {
    // Create a number input box to contain categories
    var input = document.createElement("input");
    input.type = "number";
    input.value = "0";
    input.name = numberName;
    return input;
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

    // Make sure all of the category names are up to date.
    updateCategoryNames();
}


/**
 * Setup the config div for a multiple-choice question.
 */
function setupMultiChoiceConfig(questionNumber, configDiv) {
    // The category names above each column of checkboxes.
    for (var categoryNumber = 0; categoryNumber < 4; ++categoryNumber) {
        var label = document.createElement("text");
        label.className = `check_label category_${categoryNumber}_name`;
        configDiv.appendChild(label);
    }

    // Clears away the floating from checkbox labels.
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
        input.style = "width: 80%; float: left;";

        // Add in the checkboxes
        var checkNamePrefix = `question_${questionNumber}_multi_choice_${index}`;
        var breadTypeDiv = createDiv("bread_type", [
            createCheckButton(`${checkNamePrefix}_category_1`),
            createCheckButton(`${checkNamePrefix}_category_2`),
            createCheckButton(`${checkNamePrefix}_category_3`),
            createCheckButton(`${checkNamePrefix}_category_4`)
        ]);

        // Add the text field to the config div.
        configDiv.appendChild(input);
        configDiv.appendChild(breadTypeDiv);
    }

    // Add a break to clear the floats of checkboxes
    var clearBreak2 = document.createElement("div");
    clearBreak2.className = "clear";
    configDiv.appendChild(clearBreak2);
}


/**
 * Updates the labels that contain the name of the categories when the category names change.
 */
function updateCategoryNames() {
    // First find current bread names from boxes at top of page
    var categoryInputs = document.getElementsByClassName("categories");

    // Update the name for each category.
    for (var categoryNumber = 0; categoryNumber < categoryInputs.length; ++categoryNumber) {
        var categoryName = categoryInputs[categoryNumber].value;
        if (categoryName.length === 0) {
            categoryName = "Category " + (categoryNumber + 1);
        }

        // Update all the labels that should contain this category name.
        var labels = document.getElementsByClassName(`category_${categoryNumber}_name`);
        for (var index = 0; index < labels.length; ++index) {
            var label = labels[index];
            label.innerText = categoryName;
        }
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

    // Create the div that holds the configuration for the slider itself.
    var sliderConfigDiv = createSliderPropertiesConfig(paramNamePrefix, showStep);

    // Create the div that holds the configuration for the scoring of user answers.
    var scoringConfigDiv = createSliderScoringConfig(paramNamePrefix);

    // Append the config divs to the config div.
    sliderConfigDiv.className = "left";
    scoringConfigDiv.className = "right";
    configDiv.appendChild(createDiv("flex_row", [sliderConfigDiv, scoringConfigDiv]));
}

/**
 * Creates the div that allows the configuration of just the slider properties.
 * Does not include the configuration options for the scoring of user's answers.
 */
function createSliderPropertiesConfig(paramNamePrefix, showStep) {
    var configDiv = document.createElement("div");

    // Create the min/max inputs.
    var min = document.createElement("input");
    min.type = "number";
    min.min = "0";
    min.max = "10000";
    min.value = "0";
    min.name = paramNamePrefix + "_min";
    min.id = paramNamePrefix + "_min";
    //min.style = "float: left;";
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
    min_label.innerHTML = "Minimum Value";
    max_label.innerHTML = "Maximum Value";

    // Add all the elements to the config div.
    configDiv.appendChild(min_label);
    configDiv.appendChild(document.createElement("br"));
    configDiv.appendChild(min);
    configDiv.appendChild(document.createElement("br"));
    configDiv.appendChild(max_label);
    configDiv.appendChild(document.createElement("br"));
    configDiv.appendChild(max);
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
        step_label.innerHTML = "Slider Step";

        // Add all the elements for the step config.
        configDiv.appendChild(step_label);
        configDiv.appendChild(document.createElement("br"));
        configDiv.appendChild(step);
        configDiv.appendChild(document.createElement("br"));
    }

    // Add in accuracy metric (std_dev_x) that determines the rate
    // of drop off in scores the further away an answer is from
    // the created answers.
    var error_margin = document.createElement("input");
    error_margin.type = "number";
    error_margin.min = "1";
    error_margin.max = "10000";
    error_margin.value = "1";
    error_margin.name = paramNamePrefix + "_std_dev_x";
    error_margin.id = paramNamePrefix + "_std_dev_x";

    // Create the associated label with the accuracy input
    var error_margin_label = document.createElement("label");
    error_margin_label.htmlFor = paramNamePrefix + "_std_dev_x";
    error_margin_label.innerHTML = "Margin of Error";

    configDiv.appendChild(error_margin_label);
    configDiv.appendChild(document.createElement("br"));
    configDiv.appendChild(error_margin);

    return configDiv;
}


/**
 * Creates the config div used for setting up the scoring functions
 * of users answers for each category.
 */
function createSliderScoringConfig(paramNamePrefix) {
    var configDiv = document.createElement("div");

    // Create a table for the expected answers.
    var expectedTable = document.createElement("table");
    var expectedTableHeader = document.createElement("thead");
    var expectedTableHeaderRow = document.createElement("tr");

    var expectedTableHeaderRowCategory = document.createElement("th");
    expectedTableHeaderRowCategory.innerText = "Category";
    expectedTableHeaderRow.appendChild(expectedTableHeaderRowCategory);

    var expectedTableHeaderRowValue = document.createElement("th");
    expectedTableHeaderRowValue.innerText = "Expected Value";
    expectedTableHeaderRow.appendChild(expectedTableHeaderRowValue);
    expectedTableHeader.appendChild(expectedTableHeaderRow);
    expectedTable.appendChild(expectedTableHeader);

    // Append a row for every category with its name and expected answer.
    var expectedTableBody = document.createElement("tbody");
    for (var categoryNumber = 0; categoryNumber < 4; ++categoryNumber) {
        var peakInput = createNumberBoxes(`${paramNamePrefix}_category_${categoryNumber}_peak`);
        var peakLabel = document.createElement("text");
        peakLabel.className = `category_${categoryNumber}_name`;

        var tableRow = document.createElement("tr");
        var colLabel = document.createElement("td");
        colLabel.appendChild(peakLabel);
        tableRow.appendChild(colLabel);

        var colInput = document.createElement("td");
        colInput.appendChild(peakInput);
        tableRow.appendChild(colInput);
        expectedTableBody.appendChild(tableRow);
    }
    expectedTable.appendChild(expectedTableBody);
    configDiv.appendChild(expectedTable);

    return configDiv;
}
