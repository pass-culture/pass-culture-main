/**
 * pass Culture application entry point
 */
class PcBackofficeApp {

  /** localStorage key for this application */
  static LOCALSTORAGE_KEY = 'pc'

  /** addons */
  addons = {}

  /** application state, can be partially persisted per addon using addon.saveState(state) */
  appState = {}

  /** csrfToken input will be stored here **/
  csrfToken

  /**
   * Initialize applications
   * @param {array} addOns - list of addons (class extending AddOn) to be used
   * @param {string} csrfToken - the csrf token input
   */
  constructor({ addOns: AddOns, csrfToken }) {
    this.#rehydrateState()
    this.csrfToken = csrfToken
    AddOns.forEach((AddOn) => {
      const name = `${AddOn.name[0].toLowerCase()}${AddOn.name.slice(1)}`
      this.addons[name] = new AddOn({
        name,
        app: this,
        addOnState: this.appState[name],
      })
    })
    PcUtils.addLoadEvent(this.initialize)
    PcUtils.addLoadEvent(this.bindEvents)
  }

  /**
   * initialize addon(s)
   * @example To initialize a specific addon
   * app.addons.bsTooltips.initialize()
   * @example To initialize all addons
   * app.initialize()
   */
  initialize = () => {
    Object.values(this.addons).forEach(({ initialize }) => initialize())
  }

  /**
   * bind addons events
   * @example To bind a specific addon
   * app.addons.bsTooltips.unbindEvents()
   * @example To bind all addons
   * app.bindEvents()
   */
  bindEvents = () => {
    Object.values(this.addons).forEach(({ bindEvents }) => bindEvents())
  }

  /**
   * unbind addons events
   * @example To unbind a specific addon
   * app.addons.bsTooltips.unbindEvents()
   * @example To unbind all addons
   * app.unbindEvents()
   */
  unbindEvents = () => {
    Object.values(this.addons).forEach(({ unbindEvents }) => unbindEvents())
  }

  /**
   * Persist add on state in localStorage
   * This method is public only for addons to have access to it.
   * Addons add a saveState method that allow persistence of any addon's state
   * It should not be used directly
   * @param {string} name - addon name
   * @param {any} value - addon state
   */
  _setAppState = (name, value) => {
    localStorage.setItem(
      PcBackofficeApp.LOCALSTORAGE_KEY,
      JSON.stringify({ ...this.appState, [name]: value })
    )
  }

  #rehydrateState = () => {
    this.appState = JSON.parse(localStorage.getItem(PcBackofficeApp.LOCALSTORAGE_KEY) || '{}')
  }
}
