/**
 * JS for the macro copy_to_clipboard
 */
addonList.push(
  class PcClipBoard extends PcAddOn {
    static CLIPBOARDS_SELECTOR = '.pc-clipboard'
    static TITLE_RESET_DURATION = 3000 // in millisecond

    bindEvents = () => {
      EventHandler.on(document.body, 'click', PcClipBoard.CLIPBOARDS_SELECTOR, this.#clicked)
    }

    unbindEvents = () => {
      EventHandler.off(document.body, 'click', PcClipBoard.CLIPBOARDS_SELECTOR, this.#clicked)
    }

    #clicked = (event) =>{
      event.preventDefault()
      const target = event.target.closest(PcClipBoard.CLIPBOARDS_SELECTOR)
      navigator.clipboard.writeText(target.dataset.text)
      const tooltip = bootstrap.Tooltip.getInstance(target)
      tooltip.setContent({ ".tooltip-inner": "Copié" })

      setTimeout(() => {
        if (!!tooltip._element) {  // ensure that the tooltip is still present in the dom as it might have been dismissed
          tooltip.setContent({ ".tooltip-inner": target.dataset.bsTitle })
        }
      }, PcClipBoard.TITLE_RESET_DURATION)
    }
  }
)