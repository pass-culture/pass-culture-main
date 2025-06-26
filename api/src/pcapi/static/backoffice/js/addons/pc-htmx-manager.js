/**
 * JS to handle htmx interactions while waiting for backend's response:
 *  - refresh flash messages after each htmx request
 *  - refresh tom select inside newly loaded forms
 *  - display loader spinner while loading distant content
 */

class PcHtmxManager extends PcAddOn {
  static MESSAGES_DIV = "flash-messages"
  static REFRESH_TRIGGER_EVENT = "refreshMessages"

  static LOADING_MODAL_ID = "#loading-htmx-modal"

  bindEvents = () => {
    EventHandler.on(document.body, "htmx:afterRequest", this.#triggerFetchFlashMessages)
    EventHandler.on(document.body, "htmx:afterRequest", this.#hideLoadingSpinner)
    EventHandler.on(document.body, "htmx:beforeRequest", this.#displayLoadingSpinner)
    EventHandler.on(document.body, "htmx:beforeRequest", this.app.addons.PcTomSelectFieldId.unbindEvents)
    EventHandler.on(document.body, "htmx:afterRequest", this.app.addons.PcTomSelectFieldId.bindEvents)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, "htmx:afterRequest", this.#triggerFetchFlashMessages)
    EventHandler.off(document.body, "htmx:afterRequest", this.#hideLoadingSpinner)
    EventHandler.off(document.body, "htmx:beforeRequest", this.#displayLoadingSpinner)
    EventHandler.off(document.body, "htmx:beforeRequest", this.app.addons.PcTomSelectFieldId.unbindEvents)
    EventHandler.off(document.body, "htmx:afterRequest", this.app.addons.PcTomSelectFieldId.bindEvents)
  }

  #displayLoadingSpinner = (event) => {
    const modal = bootstrap.Modal.getOrCreateInstance(PcHtmxManager.LOADING_MODAL_ID)
    const targetId = event?.detail?.target?.id
    if (!!targetId && targetId !== PcHtmxManager.MESSAGES_DIV) {
      modal.show()
    }
  }

  #hideLoadingSpinner = (event) => {
    const modal = bootstrap.Modal.getOrCreateInstance(PcHtmxManager.LOADING_MODAL_ID)
    const targetId = event?.detail?.target?.id
    modal.hide()
  }

  #triggerFetchFlashMessages = (event) => {
    const verb = event?.detail?.requestConfig?.verb
    const targetId = event?.detail?.target?.id

    if (!!targetId && targetId !== PcHtmxManager.MESSAGES_DIV) {
      htmx.trigger(`#${PcHtmxManager.MESSAGES_DIV}`, PcHtmxManager.REFRESH_TRIGGER_EVENT)
    }
  }

}
