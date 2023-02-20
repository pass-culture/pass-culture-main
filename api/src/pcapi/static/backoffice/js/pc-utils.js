class PcUtils {
  /**
   * Push a callback to window.onload
   * @param {function} callback - a function to be called on window.onload
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
   * Debounce a function
   * @param {function} callback - the function to debounce
   * @param {number} ms - debounce delay in milliseconds
   * @returns {(function(...[*]=): void)|*} - the debounced function
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

class KeyboardKeyCode {
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

