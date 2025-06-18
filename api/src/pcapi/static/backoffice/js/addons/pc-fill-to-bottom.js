/**
 * Any element with the class `pc-fill-to-bottom` will be set to a fixed size to make it fill the
 * space to the bottom of the screen without scroll
 */
class PcFillToBottom extends PcAddOn {
  static FILL_SELECTORS = '.pc-fill-to-bottom'

  get $$elements() {
    return document.querySelectorAll(PcFillToBottom.FILL_SELECTORS)
  }


  #resizeElement = () => {
    this.$$elements.forEach(($element) => {
      $element.style.height = (window.innerHeight - ($element.getBoundingClientRect().top)) + 'px' 
    })
  }

  initialize = () => {
    window.addEventListener('resize', this.#resizeElement)
    this.#resizeElement()
  }

}
