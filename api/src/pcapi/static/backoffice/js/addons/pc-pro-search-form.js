/**
 * Enables or disables departments filter depending on selected pro type.
 */
class PcProSearchForm extends PcAddOn {
  static PRO_TYPE_SELECTOR = 'form[name="pro_search"] .pc-field-pro_type select'
  static DEPARTMENTS_SELECTOR = '.pc-field-departments'

  initialize = () => {
    const $proTypeSelect = document.querySelector(PcProSearchForm.PRO_TYPE_SELECTOR)
    if ($proTypeSelect) {
      this._proTypeChange({target: $proTypeSelect})
    }
  }

  bindEvents = () => {
    EventHandler.on(document.body, 'change', PcProSearchForm.PRO_TYPE_SELECTOR, this._proTypeChange)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'change', PcProSearchForm.PRO_TYPE_SELECTOR, this._proTypeChange)
  }

  _proTypeChange = (event) => {
    const $proTypeSelect = event.target
    const $departments = document.querySelector(PcProSearchForm.DEPARTMENTS_SELECTOR)
    if ($departments) {
      if (['OFFERER', 'VENUE'].includes($proTypeSelect.value)) {
        $departments.classList.remove('d-none')
      } else {
        $departments.classList.add('d-none')
      }
    }
  }
}
