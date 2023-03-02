/**
 * This is the main entrypoint that initialize the back Office application
 * @class
 */
class PcBackofficeApp {

  /** localStorage key for this application */
  static LOCALSTORAGE_KEY = 'pc'

  /** application addons instance are available from within app  */
  addons = {}

  /** application state. It is used by PcAddOn and can be partially persisted per addon using `addon.saveState(state)` */
  appState = {}

  /** csrfToken `<input />` can be useful to generate a form with JavaScript and pass security */
  csrfToken

  /**
   * @constructor
   * @param {{ addOns: Array<PcAddOn>, csrfToken: string }} config - the application configuration
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
   * This method is automatically called on window `load` event and will run each addons initialize method.
   * When using XHR, it can be useful to rerun the initialization, or initialize a specific addon.
   * @example
   * // To manually initialize a specific addon
   * app.addons.bsTooltips.initialize()
   * @example
   * // To manually initialize all addons
   * app.initialize()
   */
  initialize = () => {
    Object.values(this.addons).forEach(({ initialize }) => initialize())
  }

  /**
   * This method is automatically called on window `load` event and will run each addons bindEvents method.
   * When using XHR, it can be useful to rerun the bindEvents method on XHR response after DOM modification.
   * @example
   * // To manually bind a specific addon
   * app.addons.bsTooltips.unbindEvents()
   * @example
   * // To manually  bind all addons
   * app.bindEvents()
   */
  bindEvents = () => {
    Object.values(this.addons).forEach(({ bindEvents }) => bindEvents())
  }

  /**
   * This method is not called automatically.
   * It run each addons unbindEvents method.
   * When using XHR, it can be useful to run the unbindEvents method prior XHR request to edit the DOM.
   * @example
   * // To manually unbind a specific addon
   * app.addons.bsTooltips.unbindEvents()
   * @example
   * // To manually unbind all addons
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
