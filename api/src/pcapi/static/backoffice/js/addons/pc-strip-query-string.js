/**
 * Strips query string from the location bar when the page is displayed.
 * This is useful for the end-user to copy a clean string without form parameter and without data used to log
 * backoffice analytics about search performance.
 */
class PcStripQueryString extends PcAddOn {
  static SELECTOR = '.pc-strip-query-string'

  initialize = () => {
    if (document.querySelector(PcStripQueryString.SELECTOR)) {
      let url = new URL(document.location.href);
      url.search = '';
      window.history.pushState({path: url.toString()}, '', url.toString());
    }
  }
}
