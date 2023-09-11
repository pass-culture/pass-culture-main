/**
 * This adds PcAddOn forbit to do multiple validations on the same form.
 * To opt out of the behavior add the class "pc-multiple-submit" to your form.
 */
class PcForm extends PcAddOn {
  static FORM_SELECTORS = 'form'
  static FORM_WHITE_LIST_CLASS = 'pc-multiple-submit'
  static FORM_ALREADY_VALIDATED = 'pc-form-validated'
  static FORM_SUBMIT_BUTTON = 'button[type=submit]'

  get $forms() {
    return document.querySelectorAll(PcForm.FORM_SELECTORS)
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'submit', PcForm.FORM_SELECTORS, this.#submit)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'submit', PcForm.FORM_SELECTORS, this.#submit)
  }

  #submit = (event) => {
    const classList = event.target.classList
    if(!classList.contains(PcForm.FORM_WHITE_LIST_CLASS))
    {
      if(classList.contains(PcForm.FORM_ALREADY_VALIDATED)){
        event.preventDefault()
      }
      else{
        classList.add(PcForm.FORM_ALREADY_VALIDATED)
        const $submitButtons = event.target.querySelectorAll(PcForm.FORM_SUBMIT_BUTTON)
        $submitButtons.forEach(($button) => {
          $button.disabled = true
        })
      }
    }
  }
}
