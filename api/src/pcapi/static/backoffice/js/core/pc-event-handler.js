// The MIT License (MIT)
//
// Copyright (c) 2011-2023 The Bootstrap Authors
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
//
//
/**
 *
 * This singleton utility class can be used to bind/unbind event in the style of `jQuery.on`/`jQuery.off`.
 *
 * It is heavily inspired from Bootstrap (v5.3.0-alpha1): `dom/event-handler.js`
 *
 * Original source: https://github.com/twbs/bootstrap/blob/cf9454caa00872899215603e5e036d9a824b1b11/js/src/dom/event-handler.js
 *
 * As the original source, this addon is licensed as MIT.
 *
 * The event will have:
 * - `event.target`: the target DOM element.
 * - `event.delegateTarget`: the parent DOM element that hold the bind.
 *
 * Each addon must have a `bindEvents` and `unbindEvent` method,
 * and can have an `initialize` method which will be called on document load.
 *
 * @example
 * // We must add DOM events using PcAddOn class.
 * class PcLoggingOnImage extend PcAddOn {
 *   bindEvents() {
 *     // bind events
 *     EventHandler.on(document.body, 'click', 'img', this.#onClick)
 *   }
 *
 *   unbindEvents() {
 *     // unbind events (revert)
 *     EventHandler.off(document.body, 'click', 'img', this.#onClick)
 *   }
 *
 *   #onClick() {
 *     console.log('Image as been clicked!')
 *   }
 * }
 *
 *
 */
class PcEventHandler {

  static #isInternalConstructing = false
  static NAMESPACE_REGEX = /[^.]*(?=\..*)\.|.*/
  static STRIP_NAME_REGEX = /\..*/
  static STRIP_UID_REGEX = /::\d+$/
  static CUSTOM_EVENTS = {
    mouseenter: 'mouseover',
    mouseleave: 'mouseout'
  }
  static NATIVE_EVENTS = new Set([
    'click',
    'dblclick',
    'mouseup',
    'mousedown',
    'contextmenu',
    'mousewheel',
    'DOMMouseScroll',
    'mouseover',
    'mouseout',
    'mousemove',
    'selectstart',
    'selectend',
    'keydown',
    'keypress',
    'keyup',
    'orientationchange',
    'touchstart',
    'touchmove',
    'touchend',
    'touchcancel',
    'pointerdown',
    'pointermove',
    'pointerup',
    'pointerleave',
    'pointercancel',
    'gesturestart',
    'gesturechange',
    'gestureend',
    'focus',
    'blur',
    'change',
    'reset',
    'select',
    'submit',
    'focusin',
    'focusout',
    'load',
    'unload',
    'beforeunload',
    'resize',
    'move',
    'DOMContentLoaded',
    'readystatechange',
    'error',
    'abort',
    'scroll'
  ])

  constructor() {
    if (!PcEventHandler.#isInternalConstructing) {
      throw new TypeError("PcEventHandler is not constructable")
    }
    this.uidEvent = 1
    this.eventRegistry = {} // Events storage
  }

  /**
   * @private
   * Create EventHandler singleton
   * @returns {PcEventHandler}
   * @example
   * const EventHandler = PcEventHandler.create()
   */
  static _create() {
    PcEventHandler.#isInternalConstructing = true
    const instance = new PcEventHandler()
    PcEventHandler.#isInternalConstructing = false
    return instance
  }

  #makeEventUid = (element, uid) => {
    return (uid && `${uid}::${uidEvent++}`) || element.uidEvent || uidEvent++
  }

  #getElementEvents = (element) => {
    const uid = this.#makeEventUid(element)

    element.uidEvent = uid
    this.eventRegistry[uid] = this.eventRegistry[uid] || {}

    return this.eventRegistry[uid]
  }

  #bootstrapHandler = (element, fn) => {
    const self = this
    return function handler(event) {
      self.#hydrateObj(event, { delegateTarget: element })

      if (handler.oneOff) {
        self.off(element, event.type, fn)
      }

      return fn.apply(element, [event])
    }
  }

  #bootstrapDelegationHandler = (element, selector, fn) => {
    const self = this
    return function handler(event) {
      const domElements = element.querySelectorAll(selector)

      for (let { target } = event; target && target !== this; target = target.parentNode) {
        for (const domElement of domElements) {
          if (domElement !== target) {
            continue
          }

          self.#hydrateObj(event, { delegateTarget: target })

          if (handler.oneOff) {
            self.off(element, event.type, selector, fn)
          }

          return fn.apply(target, [event])
        }
      }
    }
  }

  #findHandler = (events, callable, delegationSelector = null) => {
    return Object.values(events)
      .find((event) => event.callable === callable && event.delegationSelector === delegationSelector)
  }

  #normalizeParameters = (originalTypeEvent, handler, delegationFunction) => {
    const isDelegated = typeof handler === 'string'
    // todo: tooltip passes `false` instead of selector, so we need to check
    const callable = isDelegated ? delegationFunction : (handler || delegationFunction)
    let typeEvent = this.#getTypeEvent(originalTypeEvent)

    if (!PcEventHandler.NATIVE_EVENTS.has(typeEvent)) {
      typeEvent = originalTypeEvent
    }

    return [isDelegated, callable, typeEvent]
  }

  #addHandler = (element, originalTypeEvent, handler, delegationFunction, oneOff) => {
    if (typeof originalTypeEvent !== 'string' || !element) {
      return
    }

    let [isDelegated, callable, typeEvent] = this.#normalizeParameters(originalTypeEvent, handler, delegationFunction)

    // in case of mouseenter or mouseleave wrap the handler within a that checks for its DOM position
    // this prevents the handler from being dispatched the same way as mouseover or mouseout does
    if (originalTypeEvent in PcEventHandler.CUSTOM_EVENTS) {
      const wrapFunction = (fn) => {
        return (event) => {
          if (!event.relatedTarget || (event.relatedTarget !== event.delegateTarget && !event.delegateTarget.contains(event.relatedTarget))) {
            return fn.call(this, event)
          }
        }
      }

      callable = wrapFunction(callable)
    }

    const events = this.#getElementEvents(element)
    const handlers = events[typeEvent] || (events[typeEvent] = {})
    const previousFunction = this.#findHandler(handlers, callable, isDelegated ? handler : null)

    if (previousFunction) {
      previousFunction.oneOff = previousFunction.oneOff && oneOff

      return
    }

    const uid = this.#makeEventUid(callable, originalTypeEvent.replace(PcEventHandler.NAMESPACE_REGEX, ''))
    const fn = isDelegated ?
      this.#bootstrapDelegationHandler(element, handler, callable) :
      this.#bootstrapHandler(element, callable)

    fn.delegationSelector = isDelegated ? handler : null
    fn.callable = callable
    fn.oneOff = oneOff
    fn.uidEvent = uid
    handlers[uid] = fn

    element.addEventListener(typeEvent, fn, isDelegated)
  }

  #removeHandler = (element, events, typeEvent, handler, delegationSelector) => {
    const fn = this.#findHandler(events[typeEvent], handler, delegationSelector)

    if (!fn) {
      return
    }

    element.removeEventListener(typeEvent, fn, Boolean(delegationSelector))
    delete events[typeEvent][fn.uidEvent]
  }

  #removeNamespacedHandlers = (element, events, typeEvent, namespace) => {
    const storeElementEvent = events[typeEvent] || {}

    for (const [handlerKey, event] of Object.entries(storeElementEvent)) {
      if (handlerKey.includes(namespace)) {
        this.#removeHandler(element, events, typeEvent, event.callable, event.delegationSelector)
      }
    }
  }

  #getTypeEvent = (event) => {
    // allow to get the native events from namespaced events ('click.bs.button' --> 'click')
    event = event.replace(PcEventHandler.STRIP_NAME_REGEX, '')
    return PcEventHandler.CUSTOM_EVENTS[event] || event
  }

  #hydrateObj = (obj, meta = {}) => {
    for (const [key, value] of Object.entries(meta)) {
      try {
        obj[key] = value
      } catch {
        Object.defineProperty(obj, key, {
          configurable: true,
          get() {
            return value
          }
        })
      }
    }

    return obj
  }

  /**
   * Bind event for many elements with EventHandler.on
   * @description Read more: https://api.jquery.com/on/#on-events-selector-data
   * @param {element} element - the parent element to apply bind
   * @param {string} event - the event name to bind
   * @param {string} handler - the selector for elements bind apply
   * @param {function} delegationFunction - the event method to bind
   * @example
   * EventHandler.on(document.body, 'click', '.nav-link', onNavLinkClick)
   */
  on = (element, event, handler, delegationFunction) => {
    this.#addHandler(element, event, handler, delegationFunction, false)
  }

  /**
   * Bind event for a single element with EventHandler.one
   * @description Read more: https://api.jquery.com/one/#one-events-selector-data
   * @param {element} element - the parent element to apply bind
   * @param {string} event - the event name to bind
   * @param {string} handler - the selector for element bind apply
   * @param {function} delegationFunction - the event method to bind
   * @example
   * EventHandler.one(document.body, 'click', '.nav-link#something', onNavLinkClick)
   */
  one = (element, event, handler, delegationFunction) => {
    this.#addHandler(element, event, handler, delegationFunction, true)
  }

  /**
   * Unbind events attached with EventHandler.off
   * @description Read more: https://api.jquery.com/off/#off-events-selector-data
   * @param {element} element - the parent element to unbind from
   * @param {string} originalTypeEvent - the event name to unbind
   * @param {string} handler - the selector for element bind apply
   * @param {function} delegationFunction - the event method to unbind
   * @example
   * EventHandler.off(document.body, 'click', '.nav-link', onNavLinkClick)
   */
  off = (element, originalTypeEvent, handler, delegationFunction) => {
    if (typeof originalTypeEvent !== 'string' || !element) {
      return
    }

    const [isDelegated, callable, typeEvent] = this.#normalizeParameters(originalTypeEvent, handler, delegationFunction)
    const inNamespace = typeEvent !== originalTypeEvent
    const events = this.#getElementEvents(element)
    const storeElementEvent = events[typeEvent] || {}
    const isNamespace = originalTypeEvent.startsWith('.')

    if (typeof callable !== 'undefined') {
      // Simplest case: handler is passed, remove that listener ONLY.
      if (!Object.keys(storeElementEvent).length) {
        return
      }

      this.#removeHandler(element, events, typeEvent, callable, isDelegated ? handler : null)
      return
    }

    if (isNamespace) {
      for (const elementEvent of Object.keys(events)) {
        this.#removeNamespacedHandlers(element, events, elementEvent, originalTypeEvent.slice(1))
      }
    }

    for (const [keyHandlers, event] of Object.entries(storeElementEvent)) {
      const handlerKey = keyHandlers.replace(PcEventHandler.STRIP_UID_REGEX, '')

      if (!inNamespace || originalTypeEvent.includes(handlerKey)) {
        this.#removeHandler(element, events, typeEvent, event.callable, event.delegationSelector)
      }
    }
  }

  /**
   * Trigger manually an event with EventHandler.trigger
   * @description Read more: https://api.jquery.com/trigger/#trigger-events-selector-data
   * @param {element} element - DOM element to trigger event on
   * @param {string} event - The event to trigger
   * @param {*} args - Arguments to be passed to the event
   * @returns {null|Event} - null if element is undefined or event is not a string, the triggered event otherwise
   * @example
   * EventHandler.trigger(document.querySelectorAll('.nav-link')[2], 'click')
   */
  trigger = (element, event, args) => {
    if (typeof event !== 'string' || !element) {
      return null
    }

    let bubbles = true
    let nativeDispatch = true
    let defaultPrevented = false

    let evt = new Event(event, { bubbles, cancelable: true })
    evt = this.#hydrateObj(evt, args)

    if (defaultPrevented) {
      evt.preventDefault()
    }

    if (nativeDispatch) {
      element.dispatchEvent(evt)
    }

    return evt
  }
}

const EventHandler = PcEventHandler._create()
