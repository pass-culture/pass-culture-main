/**
 * This addon add support for field list (PcFieldList).
 *
 * Field list can be used to add or remove new field
 *
 */
class PcFieldList extends PcAddOn {

  static PC_FIELD_LIST_CONTAINER_SELECTOR = '[data-field-list-container]'
  static PC_FIELD_LIST_UL_SELECTOR = 'ul.field-list'
  static ADD_BUTTON_SELECTOR = '.field-list-add-btn'
  static REMOVE_BUTTON_SELECTOR = '.field-list-rm-btn'
  static FIELD_ELEMENT_BEARING_VALUE_SELECTOR = '.value-element-form'
  static FIELD_LABEL_SELECTOR = '.label-element-form'
  static EMPTY_TOM_SELECT_FORM_CONTAINER_CLASS = 'empty-tom-select-form-container'

  get $$fieldListContainer() {
    return document.querySelectorAll(PcFieldList.PC_FIELD_LIST_CONTAINER_SELECTOR)
  }


  initialize = () => {
    this.$$fieldListContainer.forEach(($fieldListContainer) => {
      this.#filterMaxEntries(this.#getUlFromContainer($fieldListContainer), true)
      this.#filterMinEntries(this.#getUlFromContainer($fieldListContainer), true)
      this.#getButtonsFromContainer($fieldListContainer).forEach(($button) => {
        $button.dataset.fieldListContainerId = $fieldListContainer.dataset.fieldListContainer
      })
    })
  }

  bindEvents = () => {
    this.initialize()
    EventHandler.on(document.body, 'click', PcFieldList.ADD_BUTTON_SELECTOR, this.#onAdd)
    EventHandler.on(document.body, 'click', PcFieldList.REMOVE_BUTTON_SELECTOR, this.#onRemove)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcFieldList.ADD_BUTTON_SELECTOR, this.#onAdd)
    EventHandler.off(document.body, 'click', PcFieldList.REMOVE_BUTTON_SELECTOR, this.#onRemove)
  }

  #getFieldListContainerFromId(fieldListContainerId) {
    return document.querySelector(`${PcFieldList.PC_FIELD_LIST_CONTAINER_SELECTOR.slice(0, -1)}=${fieldListContainerId}]`)
  }

  #getUlFromContainer($fieldListContainer) {
    return $fieldListContainer.querySelector(PcFieldList.PC_FIELD_LIST_UL_SELECTOR)
  }

  #getButtonsFromContainer($fieldListContainer) {
    return $fieldListContainer.querySelectorAll('button')
  }

  #changeButtonDisplay = ($ul, selector, shouldDisplay) => {
    const $$buttons = $ul.parentElement.querySelectorAll(selector)
    $$buttons.forEach(($button) => {
      if (shouldDisplay === true) {
        $button.classList.remove('d-none')
      } else {
        $button.classList.add('d-none')
      }
    })
  }

  #generateNextElementName = ($ul) => {
    const { fieldName: baseFieldName, entriesCount } = $ul.dataset
    const nextFieldNumber = Number(entriesCount) + 1
    $ul.dataset.entriesCount = nextFieldNumber
    return `${baseFieldName}-${nextFieldNumber}`
  }

  #filterMaxEntries = ($ul, skipError) => {
    const maxEntries = Number($ul.dataset.maxEntries)
    if (maxEntries && maxEntries !== undefined) {
      const fieldsCount = $ul.children.length
      if (fieldsCount >= maxEntries - 1) {
        this.#changeButtonDisplay($ul, PcFieldList.ADD_BUTTON_SELECTOR, "none")
      }
      if (fieldsCount >= maxEntries && !skipError) {
        throw new Error('Already max entries');
      }
    }
  }

  #filterMinEntries = ($ul, skipError) => {
    const minEntries = Number($ul.dataset.minEntries)
    if (minEntries && minEntries !== undefined) {
      const fieldsCount = $ul.children.length
      if (fieldsCount <= minEntries + 1) {
        this.#changeButtonDisplay($ul, PcFieldList.REMOVE_BUTTON_SELECTOR, "none")
      }
      if (fieldsCount <= minEntries && !skipError) {
        throw new Error('Already min entries');
      }
    }
  }

  #cloneElementFunction = ($ul) => {
    const $firstLi = $ul.firstElementChild
    const { cloneFunctionName } = $firstLi.firstElementChild.dataset
    cloneFunctionName ? this[cloneFunctionName]($ul) : this.#defaultCloneFunction($ul)
  }

  // Those methods will be referenced within many of our flask form fields
  
  _tomSelectCloneFunction = ($ul) => {
    const tomSelectClass = this.app.addons[this.app.addons.PcTomSelectFieldId.constructor.ID].constructor.PC_TOM_SELECT_FIELD_CLASS
    const $emptyForm = $ul.querySelector(`.${PcFieldList.EMPTY_TOM_SELECT_FORM_CONTAINER_CLASS}`)
    const $removeButton = $ul.querySelector(PcFieldList.REMOVE_BUTTON_SELECTOR).cloneNode(true)
    const $li = document.createElement('li')
    const $newEmptyForm = $emptyForm.cloneNode(true)
    $li.append($newEmptyForm, $emptyForm.cloneNode(true), $removeButton) // we keep a clone within the newly added and edited $newEmptyForm form
    $li.querySelector(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR).classList.add(tomSelectClass)
    this.#resetAndRenameElement($li, this.#generateNextElementName($ul))
    $ul.insertBefore($li, $ul.querySelector(PcFieldList.ADD_BUTTON_SELECTOR))
    app.addons.pcTomSelectField.rebindEvents()
    $newEmptyForm.classList.remove("d-none")
    $newEmptyForm.classList.remove(PcFieldList.EMPTY_TOM_SELECT_FORM_CONTAINER_CLASS)
  }

  #defaultCloneFunction = ($ul) => {
    const firstLi = $ul.firstElementChild
    const $li = firstLi.cloneNode(true)
    this.#resetAndRenameElement($li, this.#generateNextElementName($ul))
    $ul.insertBefore($li, $ul.querySelector(PcFieldList.ADD_BUTTON_SELECTOR))
  }
  
  
  // method will be referenced within many of our flask form fields
  #resetAndRenameElement = ($li, newName) => {
    const { resetAndRenameFunctionName } = $li.firstElementChild.dataset
    if (resetAndRenameFunctionName) {
      this[resetAndRenameFunctionName]($li, newName)
    } else {
      this.#defaultResetAndRename($li, newName)
    }
  }

  // reset functions --------------------------------------------------------------
  _resetAndRenameCheckbox = ($li, newName) => {
    const valueElement = $li.querySelector(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR)
    const label = $li.querySelector(PcFieldList.FIELD_LABEL_SELECTOR)
    valueElement.id = newName
    valueElement.name = newName
    valueElement.checked = valueElement.dataset.defaultValue
    if (label !== null) {
      label.htmlFor = newName
    }
  }

  #defaultResetAndRename = ($li, newName) => {
    const valueElement = $li.querySelector(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR)
    const label = $li.querySelector(PcFieldList.FIELD_LABEL_SELECTOR)
    valueElement.id = newName
    valueElement.name = newName
    valueElement.value = valueElement.dataset.defaultValue ? valueElement.dataset.defaultValue : ""
    if (label !== null) {
      label.htmlFor = newName
    }
  }

  #onAdd = (event) => {
    const { fieldListContainerId } = event.target.dataset
    const $fieldListContainer = this.#getFieldListContainerFromId(fieldListContainerId)
    const $ul = $fieldListContainer.querySelector(PcFieldList.PC_FIELD_LIST_UL_SELECTOR)
    this.#filterMaxEntries($ul)
    this.#cloneElementFunction($ul)
    this.#changeButtonDisplay($ul, PcFieldList.REMOVE_BUTTON_SELECTOR, true)
  }

  #onRemove = (event) => {
    const { fieldListContainerId } = event.target.dataset
    const $fieldListContainer = this.#getFieldListContainerFromId(fieldListContainerId)
    const $ul = $fieldListContainer.querySelector(PcFieldList.PC_FIELD_LIST_UL_SELECTOR)
    const $li = event.target.parentElement // remove button is within li
    this.#filterMinEntries($ul)
    $li.remove()
    this.#changeButtonDisplay($ul, PcFieldList.ADD_BUTTON_SELECTOR, true)
  }

}
