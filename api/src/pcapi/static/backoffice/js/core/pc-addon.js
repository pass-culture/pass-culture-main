/**
 * Abstract addon class is used to create application addon
 */
class PcAddOn {
  constructor({ name, app, addOnState }) {
    this.name = name
    this.app = app
    this.state = addOnState || {}
    /**
     * save addon state in localStorage
     * @param {any} state - the addon state to be persisted
     */
    this.saveState = (state) => app._setAppState(name, state)
  }

  /**
   * initialize addon
   */
  initialize() {}

  /**
   * bind addon events
   * @example
   * app.addons.bsTooltips.bindEvents()
   */
  bindEvents() {}

  /**
   * unbind addon events
   * @example
   * app.addons.bsTooltips.unbindEvents()
   */
  unbindEvents() {}


  /**
   * just a repetitive utility that prevent default event
   * @param {event} event - the event
   */
  _preventDefault(event) {
    event.preventDefault()
  }
}
