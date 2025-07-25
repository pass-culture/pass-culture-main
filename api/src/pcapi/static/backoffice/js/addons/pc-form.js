/**
 * This adds PcAddOn forbit to do multiple validations on the same form.
 * To opt out of the behavior add the class "pc-multiple-submit" to your form.
 */
class PcForm extends PcAddOn {
  static FORM_SELECTORS = 'form'
  static FORM_WHITE_LIST_CLASS = 'pc-multiple-submit'
  static FORM_ALREADY_VALIDATED = 'pc-form-validated'
  static FORM_SUBMIT_BUTTON = 'button[type=submit]'
  static FORM_MODALE_SELECTOR = '[data-modal-selector]'

  get $forms() {
    return document.querySelectorAll(PcForm.FORM_SELECTORS)
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'submit', PcForm.FORM_SELECTORS, this.#submit)
    addEventListener("pagehide", this.#unlockAll)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'submit', PcForm.FORM_SELECTORS, this.#submit)
    removeEventListener("pagehide", this.#unlockAll)
  }

  #submit = (event) => {
    const classList = event.target.classList
    if(!classList.contains(PcForm.FORM_WHITE_LIST_CLASS))
    {
      if(classList.contains(PcForm.FORM_ALREADY_VALIDATED)){
        event.preventDefault()
      }
      else{
        this.#lock(event.target)
        this.#hideModal(event.target)
      }
    }
  }

  #lock = ($target) => {
    $target.classList.add(PcForm.FORM_ALREADY_VALIDATED)
    const $submitButtons = $target.querySelectorAll(PcForm.FORM_SUBMIT_BUTTON)
    $submitButtons.forEach(($button) => {
      $button.disabled = true
    })
  }

  #unlock = ($target) => {
    $target.classList.remove(PcForm.FORM_ALREADY_VALIDATED)
    const $submitButtons = $target.querySelectorAll(PcForm.FORM_SUBMIT_BUTTON)
    $submitButtons.forEach(($button) => {
      $button.disabled = false
    })
  }

  #unlockAll = () => {
    const $lockedForms = document.querySelectorAll('.' + PcForm.FORM_ALREADY_VALIDATED)
    $lockedForms.forEach(($lockedForm) => {
      this.#unlock($lockedForm)
    })
  }

  #hideModal = ($element) => {
    const $modalSelectorElement = $element.querySelector(PcForm.FORM_MODALE_SELECTOR)
    if (!!$modalSelectorElement){
      const $modalElement = $element.closest($modalSelectorElement.dataset.modalSelector)
      if(!!$modalElement){
        const modal = bootstrap.Modal.getInstance($modalElement)
        modal.hide()
      }
    }
  }
}
