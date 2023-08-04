/**
 * JS for the macro copy_link_clipboard
 */
class PcClipBoard extends PcAddOn {
  static TOOLTIP_SELECTORS = '.pc-clipboard'
  tooltips = []

  bindEvents = () => {
    console.log("bind")
    EventHandler.on(document.body, 'click', PcClipBoard.TOOLTIP_SELECTORS, this.#clicked)
  }

  unbindEvents = () => {
    console.log("unbind")
    EventHandler.off(document.body, 'click', PcClipBoard.TOOLTIP_SELECTORS, this.#clicked)
  }
 
  #clicked = (event) =>{
    console.log("event")
    navigator.clipboard.writeText(event.target.dataset.text)
    event.target.classList.remove("bi-clipboard")
    event.target.classList.add("bi-clipboard-check")
  } 
}
