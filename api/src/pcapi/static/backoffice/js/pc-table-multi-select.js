const allIds = []
const allValidationsId = 'all-validations'
const allCheckboxes = document.querySelectorAll("input[name^='check-']")

var idValidations = [] //rows selected

function popAtIndex(array, element) { //Delete from array
    const index = array.indexOf(element);
    if (index > -1) {
        array.splice(index, 1)
    }
}
function selectAll() {
    allCheckboxes.forEach(el => {
        el.checked = true
        if (el.id !== allValidationsId) {
            idValidations.push(el.id)
        }
    })
}

function unselectAll() {
    allCheckboxes.forEach(el => {
        el.checked = false
    })
}

function disableToolbar(disable) {
    Array.from(document.getElementById("batch-buttons").children).forEach(el => {
        el.disabled = disable
    })
}

if (idValidations.length === 0) {
    disableToolbar(true)
}


allCheckboxes.forEach((el) => {
    //Initialize the array of id of all rows
    if (el.id !== allValidationsId) {
        allIds.push(el.id)
    }
    //Manage the checkbox click
    el.addEventListener("click", () => {
        if (el.checked) {
            disableToolbar(false)
            if (el.id === allValidationsId) {
                idValidations = []
                selectAll()
            } else {
                idValidations.push(el.id)
            }
        } else {
            if (el.id === allValidationsId) {
                unselectAll()
                idValidations = []
                disableToolbar(true)
            } else {
                popAtIndex(idValidations, el.id)
                if (idValidations.length === 0) {
                    disableToolbar(true)
                }
            }
        }
        //Manage The indeterminate state of select-all checkbox
        document.getElementById(allValidationsId).indeterminate = (idValidations.length < allIds.length && idValidations.length > 0)
    })
});