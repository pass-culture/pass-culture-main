/**
 * JS to handle flash messages:
 *  - refresh flash messages after each htmx request
 *  - remove flash message when they timeout
 */

class PcFlash extends PcAddOn {
  static MESSAGES_DIV = "flash-messages"
  static REFRESH_TRIGGER_EVENT = "refreshMessages"
  static ALERT_TIMEOUT = 7000

  isLoadingFlashMessages = false

  initialize = () => {
    EventHandler.on(document.body, "htmx:beforeRequest", this.#startLoadingFlashMessages)
    EventHandler.on(document.body, "htmx:afterRequest", this.#finishLoadingFlashMessages)
    EventHandler.on(document.body, "htmx:afterRequest", this.#triggerFetchFlashMessages)
    EventHandler.on(document.body, "htmx:beforeSwap", this.#displayFlashMessage)
    // add timeout for the flash setup in backend
    document.querySelectorAll('.alert').forEach(($alert) => {
      this.#flashTimeout($alert.id)
    })
  }

  #startLoadingFlashMessages = (event) => {
    const triggeringEvent = event?.detail?.requestConfig?.triggeringEvent?.type
    if (triggeringEvent === "refreshMessages") {
      this.isLoadingFlashMessages = true
    }
  }

  #finishLoadingFlashMessages = (event) => {
    const triggeringEvent = event?.detail?.requestConfig?.triggeringEvent?.type
    if (triggeringEvent === PcFlash.REFRESH_TRIGGER_EVENT) {
      this.isLoadingFlashMessages = false
    }
  }

  #displayFlashMessage = (event) => {
    const triggeringEvent = event?.detail?.requestConfig?.triggeringEvent?.type
    if (triggeringEvent === PcFlash.REFRESH_TRIGGER_EVENT) {
      const response = new DOMParser().parseFromString(event.detail.serverResponse, "text/xml");
      response.querySelectorAll('.alert').forEach(($alert) => {
        this.#flashTimeout($alert.id)
      })
    }
  }

  #flashTimeout = (id) => {
    setTimeout(() => {
      const $element = document.getElementById(id)
      if ($element !== null) {
        // do not delete the flash if the user is interacting with it
        if ( !$element.matches(":hover")){
          $element.remove()
        }
      }
    }, PcFlash.ALERT_TIMEOUT) 
  }

  fetchFlashMessages = () => {
    if (!this.isLoadingFlashMessages) {
      htmx.trigger(`#${PcFlash.MESSAGES_DIV}`, PcFlash.REFRESH_TRIGGER_EVENT)
    }
  }

  #triggerFetchFlashMessages = (event) => {
    const verb = event?.detail?.requestConfig?.verb
    const targetId = event?.detail?.target?.id
    if (!!targetId && targetId !== PcFlash.MESSAGES_DIV) {
      this.fetchFlashMessages()
    }
  }
}
