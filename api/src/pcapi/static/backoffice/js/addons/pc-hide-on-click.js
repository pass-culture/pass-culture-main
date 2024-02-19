/**
 * Hides a link on click and shows a sibling block instead
 */
class PcHideOnClick extends PcAddOn {
  static HIDE_SELECTOR = '.pc-hide-on-click'
  static SHOW_SELECTOR = '.pc-show-on-click'

  bindEvents = () => {
    EventHandler.on(document.body, 'click', PcHideOnClick.HIDE_SELECTOR, this.#onClick)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcHideOnClick.HIDE_SELECTOR, this.#onClick)
  }

  #onClick = (event) => {
    const $clicked = event.target
    $clicked.classList.add('d-none')
    const $sibling = $clicked.parentElement.querySelector(PcHideOnClick.SHOW_SELECTOR)
    $sibling.classList.remove('d-none')
  }
}
