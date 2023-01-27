function manageTextAreaKeydown(event) {
    const elementId = event.target.id.replace('-textarea', '')
    const returnButton = document.getElementById(elementId + '-newline')
    const customForm = document.getElementById(elementId + '-form')
    if (event.keyCode === 13) {
        event.preventDefault();
        if (event.ctrlKey || event.shiftKey) {
            manageReturnButton(event)
        } else {
            customForm.submit();
        }
        return false;
    }
}

function manageReturnButton(event) {
    const elementId = event.target.id.replace('-newline', '')
    const textarea = document.getElementById(elementId + '-textarea')
    const start = textarea.selectionStart
    textarea.value = textarea.value.slice(0, start) + "\n" + textarea.value.slice(textarea.selectionEnd)
    textarea.setSelectionRange(start + 1, start + 1)
    textarea.focus()
}