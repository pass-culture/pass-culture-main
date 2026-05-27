/**
 * JS for tracing on tabs click in BO
 */
addonList.push(
  class PcAnalytics extends PcAddOn {
    static TAB_SELECTORS = '[data-bs-toggle="tab"]'
    static FORM_SELECTOR = '#analytics-form'

    get href() {
      return window.location.origin + window.location.pathname
    }

    get $htmxForm() {
      return document.querySelector(PcAnalytics.FORM_SELECTOR)
    }

    bindEvents = () => {
      EventHandler.on(document.body, 'click', PcAnalytics.TAB_SELECTORS, this.#tabClicked)
    }

    unbindEvents = () => {
      EventHandler.off(document.body, 'click', PcAnalytics.TAB_SELECTORS, this.#tabClicked)
    }

    #logEvent = (type, name) => {
      const $form = this.$htmxForm
      $form.querySelector('[name="type"]').value = type
      $form.querySelector('[name="name"]').value = name
      $form.querySelector('[name="origin"]').value = this.href
      $form.querySelector('[name="submit"]').click()
    }

    #tabClicked = (event) => {
      const tab = event.target.closest(PcAnalytics.TAB_SELECTORS)
      this.#logEvent('tabClicked', tab.innerHTML)
    }
  }
)