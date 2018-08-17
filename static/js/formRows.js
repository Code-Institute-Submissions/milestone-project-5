// Note that autocomplete functions are found on page scripts 

function addOrRemoveCategory() {
    // functionality to add or remove category row on
    //press of add or remove button 
    let categoryCount = 0;

    // for edit page
    // adjusts count to reflect number of existing recipe categories 
    for (let i = 1; i < 15; i++) {
        if ($(`#category-${i}`).length > 0) {
            categoryCount = i;
        }
    }

    $("#add-category").click(function() {
        $(`#category-${categoryCount}`).after(`
                 <input type="text" name="category-${++categoryCount}" id="category-${categoryCount}" class="autocomplete categoriesAutocomplete">
                `);
        autocompleteFunction();
    });
    $("#remove-category").click(function() {
        if (categoryCount > 0) {
            $(`#category-${categoryCount}`).remove();
            categoryCount--;
        }
    });
}


function addOrRemoveIngredient() {
    let ingredientCount = 0;
    for (let i = 0; i < 15; i++) {
        if ($(`#ingredient-${i}`).length > 0) {
            ingredientCount = i;
        }
    }

    $("#add-ingredient").click(function() {
        $(".ingredient-btn-row").before(`
                    <div class="row ingredient-row ingredient-row-${++ingredientCount}">
                         <div class="input-field col s4">
                            <label for="quantity">Quantity</label>
                            <input type="text" name="quantity-${ingredientCount}" id="quantity-${ingredientCount}" >
                    </div>
                    <div class="input-field col s4">
                        <label for="ingredient">Ingredient</label>
                        <input type="text" name="ingredient-${ingredientCount}" id="ingredient-${ingredientCount}" class="autocomplete ingredientsAutocomplete">
                    </div>
                  </div>
                `);
        //called here so that function reloads after new ingredient 
        //is added. Enables autocomplete for added rows
        autocompleteFunction();
    });

    //same functionality but for filter section of index page
    $("#add-filter-ingredient").click(function() {
        $(this).before(`
              <div class="row ingredient-row ingredient-row-${++ingredientCount}">
                    <div class="input-field col s12">
                        <label for="ingredient">Ingredient</label>
                        <input type="text" name="ingredient-${ingredientCount}" id="ingredient-${ingredientCount}" class="autocomplete ingredientsAutocomplete">
                    </div>
                    
                  </div>
                `);
        autocompleteFunction();
    });
    $("#remove-ingredient").click(function() {
        if (ingredientCount > 0) {
            $(`.ingredient-row-${ingredientCount}`).remove();
            ingredientCount--;
        }
    });
}

function addOrRemoveInstruction() {
    let instructionCount = 1;

    for (let i = 1; i < 15; i++) {
        if ($(`#instruction-${i}`).length > 0) {
            instructionCount = i;
        }
    }

    $("#add-instruction").click(function() {
        $(".instruction-btn-row").before(`  <div class = "row instruction-row-${++instructionCount}"><li>
                    <div class="instruction-input-field col s10">
                        <textarea id="instruction-${instructionCount}" name= "instruction-${instructionCount}" class="materialize-textarea"></textarea>
                    </div>

            </li></row>`);
    });

    $("#remove-instruction").click(function() {
        if (instructionCount > 1) {
            $(`.instruction-row-${instructionCount--}`).remove();
        }
    });
}

$(document).ready(function() {
    addOrRemoveCategory();
    addOrRemoveIngredient();
    addOrRemoveInstruction();
});