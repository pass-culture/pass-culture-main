/**
 * This edits the  default `submit` event on forms.
 * It internally runs `form.checkValidity()` first and aborts in case of invalid form.
 *
 * > There is no markup necessary as this selects all `<form />`
 */
class PcFormsCheckValidity extends PcAddOn {
  static FORM_SELECTOR = 'form'

  bindEvents = () => {
    EventHandler.on(document.body, 'submit', PcFormsCheckValidity.FORM_SELECTOR, this.#onFormSubmit)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'submit', PcFormsCheckValidity.FORM_SELECTOR, this.#onFormSubmit)
  }

  #onFormSubmit = (event) => {
    const $form = event.target
    if (!$form.checkValidity()) {
      event.preventDefault()
    }
  }
}
