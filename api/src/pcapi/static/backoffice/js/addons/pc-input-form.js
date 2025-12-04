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
    const $container = event.target.parentElement
    let $target = $container.querySelector('INPUT')
    if(!!$target) {
      $target.value=""
      return
    }
    $target = $container.querySelector('TEXTAREA')
    if(!!$target) {
      $target.value=""
      const $counter = $container.querySelector('.pc-textarea-counter-container')
      if (!! $counter)
        $counter.textContent = '0'

      return
    }
  }
}
