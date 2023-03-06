// This file musts contains only static utilities

/**
 * This abstract class is used to create new utilities.
 * It uses a protection to prevent using anything but static methods.
 * @example
 * // To create a new utility:
 * class PcNewToolBox extends NonConstructableUtils {
 *   static doSomething() {
 *     return "do"
 *   }
 * }
 * @example
 * // usage
 * PcNewToolBox.doSomething()
 * // fail
 * new PcNewToolBox()
 */
class NonConstructableUtils {
  static #isInternalConstructing = false

  constructor() {
    if (!NonConstructableUtils.#isInternalConstructing) {
      throw new TypeError(`${this.constructor.name} is not constructable`)
    }
  }
}

/**
 * This class is used to store transversal application utilities.
 */
class PcUtils extends NonConstructableUtils {
  /**
   * Push a callback function to window.onload
   * @param {function} callback - the function to be called on `window.onload`
   */
  static addLoadEvent(callback) {
    const fn = window.onload
    window.onload = () => {
      if (fn) {
        fn()
      }
      callback()
    }
  }

  /**
   * Debounce a function (prevents function to be called until a certain delay. Can be useful for autocompletion)
   * @param {function} callback - the function to debounce
   * @param {number} ms - the debounce delay in milliseconds
   * @returns {function} - the debounced function
   */
  static debounce(callback, ms) {
    let timeoutId = null
    return (...args) => {
      window.clearTimeout(timeoutId)
      timeoutId = window.setTimeout(() => {
        callback.apply(null, args)
      }, ms)
    }
  }

}

/**
 * Store some useful JavaScript Keyboard events keycode statically
 *
 * @example
 * // return 13
 * KeyboardKeyCode.ENTER
 */
class KeyboardKeyCode extends NonConstructableUtils {
  static ENTER = 13
  static SHIFT = 16
  static CTRL = 17
  static PAGEUP = 33
  static PAGEDOWN = 34
  static END = 35
  static HOME = 36
  static LEFT = 37
  static UP = 38
  static RIGHT = 39
  static DOWN = 40
}

