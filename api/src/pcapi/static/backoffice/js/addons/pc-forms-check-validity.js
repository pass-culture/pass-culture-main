/**
 * Addon for checking validity client side of forms prior submit
 * It works with all <form />
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
    event.preventDefault()
    const $form = event.target
    if ($form.checkValidity()) {
      $form.submit()
    }
  }
}
