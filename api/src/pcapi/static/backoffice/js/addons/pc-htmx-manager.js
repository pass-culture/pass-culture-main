/**
 * JS to handle htmx interactions while waiting for backend's response:
 *  - refresh flash messages after each htmx request
 *  - refresh tom select inside newly loaded forms
 *  - display loader spinner while loading distant content
 */

class PcHtmxManager extends PcAddOn {
  static MESSAGES_DIV = "flash-messages"
  static REFRESH_TRIGGER_EVENT = "refreshMessages"

  static LOADING_MODAL_ID = "loading-htmx-modal"
  isLoadingFlashMessages = false

  initialize = () => {
    EventHandler.on(document.body, "htmx:beforeRequest", this.#displayLoadingSpinner)

    EventHandler.on(document.body, "htmx:beforeRequest", this.#startLoadingFlashMessages)
    EventHandler.on(document.body, "htmx:afterRequest", this.#finishLoadingFlashMessages)

    EventHandler.on(document.body, "htmx:afterRequest", this.#reloadPageOnUnauthorizedError)
    EventHandler.on(document.body, "htmx:afterRequest", this.#hideLoadingSpinner)
    EventHandler.on(document.body, "htmx:afterRequest", this.#hideParentModalOnError)
    EventHandler.on(document.body, "htmx:afterRequest", this.#triggerFetchFlashMessages)
    EventHandler.on(document.body, "htmx:beforeSwap", this.app.addons.pcTableManager.applyConfigurationOnLoadedLines)
    EventHandler.on(document.body, "htmx:afterRequest", this.app.bindEvents)
    EventHandler.on(document.body, "htmx:beforeRequest", this.app.unbindEvents)
  }

  #reloadPageOnUnauthorizedError = (event) => {
    const responseStatusCode = event?.detail?.xhr?.status
    if (responseStatusCode === 401) {
      window.location.reload()
    }
  }

  #startLoadingFlashMessages = (event) => {
    const triggeringEvent = event?.detail?.requestConfig?.triggeringEvent?.type
    if (triggeringEvent === "refreshMessages") {
      this.isLoadingFlashMessages = true
    }
  }

  #finishLoadingFlashMessages = (event) => {
    const triggeringEvent = event?.detail?.requestConfig?.triggeringEvent?.type
    if (triggeringEvent === "refreshMessages") {
      this.isLoadingFlashMessages = false
    }
  }

  #hideParentModalOnError = (event) => {
    const { hideParentModalOnError } = event?.target?.dataset ?? {}
    const hasRequestFailed = event?.detail?.failed
    const $parentModal = event?.target?.closest(".modal")
    if (hideParentModalOnError && hasRequestFailed && !!$parentModal) {
      const modal = bootstrap.Modal.getInstance(`#${$parentModal.id}`)
      $parentModal.addEventListener("shown.bs.modal", event => {
        modal.hide()
      }, { once: true })
      $parentModal.addEventListener("hidden.bs.modal", event => {
        this.#fetchFlashMessages()
      }, {once: true })
    }
  }

  #displayLoadingSpinner = (event) => {
    const modal = bootstrap.Modal.getInstance(`#${PcHtmxManager.LOADING_MODAL_ID}`)
    const targetId = event?.detail?.target?.id
    if (!!targetId && targetId !== PcHtmxManager.MESSAGES_DIV && modal) {
      modal.show()
    }
  }

  #hideLoadingSpinner = (event) => {
    const $modal = document.getElementById(PcHtmxManager.LOADING_MODAL_ID)
    if (!!$modal) {
      const modal = bootstrap.Modal.getInstance(`#${PcHtmxManager.LOADING_MODAL_ID}`)
      $modal.addEventListener("shown.bs.modal", event => {
        modal.hide()
      })
    }
  }

  #fetchFlashMessages = () => {
    if (!this.isLoadingFlashMessages) {
      htmx.trigger(`#${PcHtmxManager.MESSAGES_DIV}`, PcHtmxManager.REFRESH_TRIGGER_EVENT)
    }
  }

  #triggerFetchFlashMessages = (event) => {
    const verb = event?.detail?.requestConfig?.verb
    const targetId = event?.detail?.target?.id

    if (!!targetId && targetId !== PcHtmxManager.MESSAGES_DIV) {
      this.#fetchFlashMessages()
    }
  }

}
