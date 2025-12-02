/**
 * This class tricks the default event of a `<textarea />` by submitting the form on <kbd>ENTER</kbd>,
 * and optionnally goes to the next line on <kbd>CTRL</kbd>+<kbd>ENTER</kbd> or <kbd>SHIFT</kbd>+<kbd>ENTER</kbd>.
 * @example
 * <textarea class="pc-override-custom-textarea-enter" data-allow-line-breaks="true"></textarea>
 * <textarea class="pc-override-custom-textarea-enter" data-allow-line-breaks="false"></textarea>
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
    const allowLineBreaks = Boolean($textarea.dataset.allowLineBreaks)
    if (event.keyCode === KeyboardKeyCode.ENTER) {
      event.preventDefault()
      if (allowLineBreaks && (event.ctrlKey || event.shiftKey)) {
        const { selectionStart: start, value, selectionEnd } = $textarea
        $textarea.value = `${value.slice(0, start)}\n${value.slice(selectionEnd)}`
        $textarea.setSelectionRange(start + 1, start + 1)
        $textarea.focus()
        return
      }
      $textarea.form.requestSubmit()
    }
  }
}
