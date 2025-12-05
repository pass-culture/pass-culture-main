/**
 * JS for adding a button to clear an input
 */
class PcInputForm extends PcAddOn {
    static INPUT_SELECTOR = '.pc-clear-input'

  bindEvents = () => {
    EventHandler.on(document.body, 'click', PcInputForm.INPUT_SELECTOR, this.#clicked)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcInputForm.INPUT_SELECTOR, this.#clicked)
  }

  #clicked = (event) =>{
    event.preventDefault()
    const $target = event.target.parentElement.querySelector('INPUT')
    if(!!$target) {
      $target.value=""
    }
  }
}
