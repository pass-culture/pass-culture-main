/**
 * JS for the macro copy_to_clipboard
 */
class PcClipBoard extends PcAddOn {
  static TOOLTIP_SELECTORS = '.pc-clipboard'
  static TITLE_RESET_DURATION = 3000 // in millisecond

  bindEvents = () => {
    EventHandler.on(document.body, 'click', PcClipBoard.TOOLTIP_SELECTORS, this.#clicked)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcClipBoard.TOOLTIP_SELECTORS, this.#clicked)
  }

  #clicked = (event) =>{
    event.preventDefault()
    navigator.clipboard.writeText(event.target.dataset.text)
    const tooltip = bootstrap.Tooltip.getInstance(event.target)
    tooltip.setContent({ ".tooltip-inner": "Copié" })

    setTimeout(() => {
      if (!!tooltip._element) {  // ensure that the tooltip is still present in the dom as it might have been dismissed
        tooltip.setContent({ ".tooltip-inner": event.target.dataset.bsTitle })
      }
    }, PcClipBoard.TITLE_RESET_DURATION)
  }
}
