/**
 * Add on that remove the submit on enter for line break on enter
 * Also support line break button
 * @example disable submit on enter for line break on enter
 * <textarea class="pc-override-custom-textarea-enter"></textarea>
 * @example line break button
 * <button type="button" class="pc-override-custom-textarea-enter-line-break">Do a line break</button>
 */
class PcOverrideCustomTextareaEnter extends PcAddOn {
  static TEXTAREA_SELECTOR = '.pc-override-custom-textarea-enter'
  static BUTTON_SELECTOR = '.pc-override-custom-textarea-enter-line-break'

  bindEvents = () => {
    EventHandler.on(document.body, 'keydown', PcOverrideCustomTextareaEnter.TEXTAREA_SELECTOR, this.#manageTextAreaKeydown)
    EventHandler.on(document.body,'click', PcOverrideCustomTextareaEnter.BUTTON_SELECTOR, this.#manageReturnButton)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'keydown', PcOverrideCustomTextareaEnter.TEXTAREA_SELECTOR, this.#manageTextAreaKeydown)
    EventHandler.off(document.body,'click', PcOverrideCustomTextareaEnter.BUTTON_SELECTOR, this.#manageReturnButton)
  }

  #manageTextAreaKeydown = (event) => {
    const { formName } = event.target.dataset
    const form = document.querySelector(`form[name="${formName}"]`)
    if (event.keyCode === KeyboardKeyCode.ENTER) {
      event.preventDefault()
      if (event.ctrlKey || event.shiftKey) {
        this.#manageReturnButton(event)
        return
      }
      form.submit()
    }
  }

  #manageReturnButton = (event) => {
    const { formName } = event.target.dataset
    const { comment: textarea } = document.querySelector(`form[name="${formName}"]`)
    const { selectionStart: start, value, selectionEnd } = textarea
    textarea.value = `${value.slice(0, start)}\n${value.slice(selectionEnd)}`
    textarea.setSelectionRange(start + 1, start + 1)
    textarea.focus()
  }
}
