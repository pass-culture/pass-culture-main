/**
 * This addon adds support for form field (PcFormField).
 *
 * Form fields can be used to group multiple fields into one.
 *
 */
class PcFormField extends PcAddOn {
  static ID = 'PCFormFieldId'
  static PC_FORM_FIELD_FIELD_CLASS = 'pc-form-field-field'
  static PC_FORM_FIELD_FIELD_EMPTY_SELECTOR = '.pc-form-field-empty-container'
  static PC_REQUIRED_SELECTOR = '.pc-required'

  initialize = () => {
    this.formFieldEmpty.forEach(($emptyFormField) => {
      $emptyFormField.querySelectorAll(PcFormField.PC_REQUIRED_SELECTOR).forEach(($requiredField) => {
        $requiredField.required = false
      })
      $emptyFormField.querySelectorAll(this.app.addons.PCFieldListId.constructor.FIELD_ELEMENT_BEARING_VALUE_SELECTOR).forEach(($valueElementForm) => {
        $valueElementForm.removeAttribute("name")
        $valueElementForm.removeAttribute("id")
      })
    })
    this._hideUnselectedFieldsAll()
  }

  get formFieldEmpty() {
    return document.querySelectorAll(PcFormField.PC_FORM_FIELD_FIELD_EMPTY_SELECTOR)
  }

  bindEvents = () => {
    this.initialize()
    EventHandler.on(document.body, 'change', `.${PcFormField.PC_FORM_FIELD_FIELD_CLASS} > .pc-select-with-placeholder`, this.#redrawFields)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'change', `.${PcFormField.PC_FORM_FIELD_FIELD_CLASS} > .pc-select-with-placeholder`, this.#redrawFields)
  }

  #redrawFields = ($event) => {
    const $formField = event.target.closest(`.${PcFormField.PC_FORM_FIELD_FIELD_CLASS}`)
    this._hideUnselectedFields($formField)
  }

  _retrieveConfiguration = ($formField) => {
    // configuration is only used in formFieldList, standalone formFields do not require it
    const configStr = document.querySelector(`.${$formField.dataset.configurationClass}`).innerText
    if (!!configStr){
      return JSON.parse(configStr)
    }
    return false
  }

  _hideUnselectedFieldsAll = () => {
    document.querySelectorAll(`.${PcFormField.PC_FORM_FIELD_FIELD_CLASS}`).forEach(($formField) => {
      this._hideUnselectedFields($formField)
    })
  }

  _hideUnselectedFields = ($formField) => {
    // hide all fields
    const configuration = this._retrieveConfiguration($formField)
    if (!configuration){
      // configuration is only used in formFieldList, standalone formFields do not require it
      return
    }
    const baseName = $formField.dataset.baseName
    configuration.all_available_fields.forEach((fieldTermination) => {
      const fieldName = `${baseName}-${fieldTermination}`
      const $field = $formField.querySelector(`.${fieldName}`)
      if (!$field){
        console.error(`${fieldName} not found`)
      }
      $field.classList.add('d-none')
    })
    // hide operator fields
    const operatorFieldName = `${baseName}-${configuration.operator_field_name}`
    const $operatorField = $formField.querySelector(`.${operatorFieldName}`)
    $operatorField.querySelectorAll('option').forEach(($option) => {
      if ($option.value !== '') {
        $option.classList.add('d-none')
      }
    })
    $operatorField.classList.add('d-none')
    // get selected rule
    const subRuleTypeName = `${baseName}-${configuration.sub_rule_type_field_name}`
    const $subRuleType = $formField.querySelector(`.${subRuleTypeName}`).firstElementChild
    const selectedRuleConfiguration = configuration.display_configuration[$subRuleType.value]
    // display pertinent field and operator options
    if (selectedRuleConfiguration !== undefined) {
      const selectedFieldName = `${baseName}-${selectedRuleConfiguration.field}`
      const $selectedField = $formField.querySelector(`.${selectedFieldName}`)
      $selectedField.classList.remove('d-none')
      $operatorField.classList.remove('d-none')
      $operatorField.querySelectorAll('option').forEach(($option) => {
        if (selectedRuleConfiguration.operator.includes($option.value)) {
          $option.classList.remove('d-none')
        }
      })
      const $operatorFieldSelect = $operatorField.querySelector('select')
      if (!selectedRuleConfiguration.operator.includes($operatorFieldSelect.value)) {
        $operatorFieldSelect.value = selectedRuleConfiguration.operator[0]
      }


    }
  }
}
