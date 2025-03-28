/**
 * Set focus on designated section on page load when having scrollspy navbars (details pages)
 */
class PcSectionFocusOnload extends PcAddOn {
  static SCROLLSPY_SELECTOR = '[data-bs-spy="scroll"]'
  static SELECTOR = '[data-bs-spy="scroll"]>.focus'

  bindEvents = () => {
    let $sections = document.querySelectorAll(PcSectionFocusOnload.SELECTOR)
    let $section = null
    const windowHash = window.location.hash
    if (!!$sections && $sections.length === 1) {
      $section = $sections[0].scrollIntoView()
    } else if (windowHash) {
      const $scrollspy = document.querySelectorAll(PcSectionFocusOnload.SCROLLSPY_SELECTOR)
      if (!!$scrollspy && $scrollspy.length === 1 && !!windowHash) {
        $sections = document.querySelectorAll(windowHash)
        if (!!$sections && $sections.length === 1) {
          $section = $sections[0]
        }
      }
    }
    if (!!$section) {
      $section.scrollIntoView()
      window.scrollTo(0, 0)  // hack to have only the scrollable div scrolled
    }

  }
}
