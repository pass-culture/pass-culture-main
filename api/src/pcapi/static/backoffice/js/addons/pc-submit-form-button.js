/**
 * This add-on allows to a designated button to submit a form given its name
 * It's generally used to submit hidden forms
 */
class PcSubmitFormButton extends PcAddOn {
  static SUBMIT_BUTTON_SELECTOR = "[data-submit-form]"

  bindEvents = () => {
    EventHandler.on(document.body, "click", PcSubmitFormButton.SUBMIT_BUTTON_SELECTOR, this.#onClick)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, "click", PcSubmitFormButton.SUBMIT_BUTTON_SELECTOR, this.#onClick)
  }

  #onClick = (event) => {
    const formName = event.target.dataset.submitForm
    if (!!formName) {
      const forms = document.querySelectorAll(`form[name=${formName}]`)
      if (forms.length === 1) {
        const form = forms[0]
        form.submit()
      }
    }
  }

}
