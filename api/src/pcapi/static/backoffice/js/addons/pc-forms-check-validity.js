/**
 * This edits the  default `submit` event on forms.
 * It internally runs `form.checkValidity()` first and aborts in case of invalid form.
 *
 * The add on also include a fix for tom select js to support `readonly` attribute.
 *
 * > There is no markup necessary as this selects all `<form />`
 */
class PcFormsCheckValidity extends PcAddOn {
  static FORM_SELECTOR = 'form'
  static TOM_SELECT_READ_ONLY_FIX_SELECTOR = '[data-tom-select-readonly]'

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
    this.#applyTomSelectReadonly($form)
  }

  #applyTomSelectReadonly = ($form) => {
    $form.querySelectorAll(PcFormsCheckValidity.TOM_SELECT_READ_ONLY_FIX_SELECTOR).forEach(($select) => {
      $select.disabled = false
    })
  }
}
