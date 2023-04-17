/**
 * This abstract class can be extended to create new addon for new JavaScript features.
 *
 * **It is mandatory to use it each time one needs to add JavaScript features!**
 *
 * @example
 * class ExampleAddOn extend PcAddOn {
 *   initialize() {
 *     // prepare the DOM if necessary
 *   }
 *   bindEvents() {
 *     // bind events
 *     EventHandler.on(document.body, 'click', this.#onClick)
 *   }
 *
 *   unbindEvents() {
 *     // unbind events (revert)
 *     EventHandler.off(document.body, 'click', this.#onClick)
 *   }
 * }
 * @example
 * // Add it to your app addons:
 * const app = new PcBackofficeApp({
 *   addOns: [
 *     ExampleAddOn, // <-- This is how you mount a new addon into the application.
 *   ]
 * })
 */
class PcAddOn {

  /**
   * @constructor
   * @param {{ name: string, app: PcBackofficeApp, addOnState: any }} config - the addon configuration
   */
  constructor({ name, app, addOnState }) {
    this.name = name
    this.app = app
    this.state = addOnState || {}
    /**
     * This method saves the addon's new state in localStorage
     * @param {any} state - the addon new state to be persisted
     * @example
     * // within the addon
     * this.saveState(this.state)
     * @example
     * // outside the addon
     * app.addons[name].saveState(newState)
     */
    this.saveState = (state) => app._setAppState(name, state)
  }

  /**
   * This method initializes the addon.
   * Initialization is already called on document load through instance of `PcBackofficeApp`
   */
  initialize() { }

  /**
   * This method binds addon events.
   * Initialization is already called on document load through instance of `PcBackofficeApp`.
   * It is called when event `turbo:frame-render` is emitted, prior an XHR call.
   * @example
   * app.addons.bsTooltips.bindEvents()
   */
  bindEvents() { }

  /**
   * This method unbinds addon events.
   * It is called when event `turbo:before-frame-render` is emitted, after an XHR call.
   * @example
   * app.addons.bsTooltips.unbindEvents()
   */
  unbindEvents() { }


  /**
   * This method is just a repetitive utility that prevents default event.
   * Can be useful to prevent code duplication between addons when you only need to prevent default event.
   * @param {event} event - the event
   */
  _preventDefault(event) {
    event.preventDefault()
  }

  /**
   * This method is just a repetitive utility that prevents default event when keypress is Enter.
   * Can be useful to prevent code duplication between addons when you only need to prevent default event.
   * @param {event} event - the event
   */
  _preventSubmitOnEnter = (event) => {
    const code = event.keyCode || event.which
    if (code === KeyboardKeyCode.ENTER) {
      event.preventDefault()
    }
  }
}
