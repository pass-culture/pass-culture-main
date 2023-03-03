/**
 * Add on that remove the submit on enter for line break on enter
 * Also support line break button
 * @example
 * // disable submit on enter for line break on enter
 * <textarea class="pc-override-custom-textarea-enter"></textarea>
 */
class PcOverrideCustomTextareaEnter extends PcAddOn {
  static TEXTAREA_SELECTOR = '.pc-override-custom-textarea-enter'

  bindEvents = () => {
    EventHandler.on(document.body, 'keydown', PcOverrideCustomTextareaEnter.TEXTAREA_SELECTOR, this.#manageTextAreaKeydown)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'keydown', PcOverrideCustomTextareaEnter.TEXTAREA_SELECTOR, this.#manageTextAreaKeydown)
  }

  #manageTextAreaKeydown = (event) => {
    const $textarea = event.target
    if (event.keyCode === KeyboardKeyCode.ENTER) {
      event.preventDefault()
      if (event.ctrlKey || event.shiftKey) {
        const { selectionStart: start, value, selectionEnd } = $textarea
        $textarea.value = `${value.slice(0, start)}\n${value.slice(selectionEnd)}`
        $textarea.setSelectionRange(start + 1, start + 1)
        $textarea.focus()
        return
      }
      $textarea.form.submit()
    }
  }
}