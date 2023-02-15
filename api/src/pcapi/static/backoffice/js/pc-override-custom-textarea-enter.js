/**
 * @summary Submit on enter on textarea with line break button support
 * @description Use enter to submit the form, and a button to do line break
 * The `<textarea>` attribute name must be `comment`, it must be in a `<form>` with also an attribute name,
 * The line break `<button>` and `<textarea>` must have some minimal dataset in order to work.
 * See example below.
 *
 * @example
 *
 * ```html
 * <form name="example-form">
 *   <textarea
 *     data-form-name="example-form"
 *     onkeydown="pcOverrideCustomTextareaEnter.manageTextAreaKeydown(event)"
 *   >
 *   <button
 *     data-form-name="example-form"
 *     onclick="pcOverrideCustomTextareaEnter.manageReturnButton(event)"
 *     type="button"
 *   >
 *     ⏎
 *   </button>
 * </form>
 * ```
 */
class PcOverrideCustomTextareaEnter {
    static ENTER_KEY_CODE = 13

    manageTextAreaKeydown = (event) => {
        const { formName } = event.target.dataset
        const form = document.querySelector(`[name="${formName}"]`)
        if (event.keyCode === PcOverrideCustomTextareaEnter.ENTER_KEY_CODE) {
            event.preventDefault();
            if (event.ctrlKey || event.shiftKey) {
                this.manageReturnButton(event)
                return
            }
            form.submit()
        }
    }

    manageReturnButton = (event) => {
        const { formName } = event.target.dataset
        const { comment: textarea } = document.querySelector(`form[name="${formName}"]`)
        const { selectionStart: start, value, selectionEnd } = textarea
        textarea.value = `${value.slice(0, start)}\n${value.slice(selectionEnd)}`
        textarea.setSelectionRange(start + 1, start + 1)
        textarea.focus()
    }
}

const pcOverrideCustomTextareaEnter = new PcOverrideCustomTextareaEnter()
