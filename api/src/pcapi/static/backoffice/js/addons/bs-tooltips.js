/**
 * This adds PcAddOn support for bootstrap 5 tooltips.
 * It works using bootstrap 5 html markup.
 * Read documentation: https://getbootstrap.com/docs/5.0/components/tooltips/#examples
 */
class BsTooltips extends PcAddOn {
  static TOOLTIP_SELECTORS = '[data-bs-toggle="tooltip"]'
  tooltips = []

  get $tooltips() {
    return document.querySelectorAll(BsTooltips.TOOLTIP_SELECTORS)
  }

  bindEvents = () => {
    this.$tooltips.forEach(($tooltip) => {
      this.tooltips.push(new bootstrap.Tooltip($tooltip))
    })
    // Fix the case where a button has a tooltip and displays a modal once clicked → the tooltip must hide and not stay there forever
    addEventListener("show.bs.modal", () => {
      this.tooltips.forEach((tooltip) => {
        tooltip.hide()
      })
    })
  }

  unbindEvents = () => {
    this.tooltips.forEach((tooltip) => {
      tooltip.disable()
    })
  }
}
