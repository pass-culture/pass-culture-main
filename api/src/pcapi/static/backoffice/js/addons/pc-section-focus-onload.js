/**
 * Set focus on designated section on page load when having scrollspy navbars (details pages)
 */
class PcSectionFocusOnload extends PcAddOn {
  static SELECTOR = '[data-bs-spy]>.focus'

  bindEvents = () => {
    const $sections = document.querySelectorAll(PcSectionFocusOnload.SELECTOR)
    if (!!$sections && $sections.length === 1) {
      $sections[0].scrollIntoView()
      window.scrollTo(0, 0)  // hack to have only the scrollable div scrolled
    }
  }
}
