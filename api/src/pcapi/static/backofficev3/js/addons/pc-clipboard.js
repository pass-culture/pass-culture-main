/**
 * JS for the macro copy_to_clipboard
 */
class PcClipBoard extends PcAddOn {
  static TOOLTIP_SELECTORS = '.pc-clipboard'
  tooltips = []

  bindEvents = () => {
    EventHandler.on(document.body, 'click', PcClipBoard.TOOLTIP_SELECTORS, this.#clicked)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcClipBoard.TOOLTIP_SELECTORS, this.#clicked)
  }
 
  #clicked = (event) =>{
    navigator.clipboard.writeText(event.target.dataset.text)
    event.target.classList.remove("bi-stickies")
    event.target.classList.add("bi-stickies-fill")
  } 
}
