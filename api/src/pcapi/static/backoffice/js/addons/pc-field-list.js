/**
 * This addon adds support for field list (PcFieldList).
 *
 * Field list can be used to add or remove new field
 *
 */
class PcFieldList extends PcAddOn {

  static ID = 'PCFieldListId'
  static PC_FIELD_LIST_CONTAINER_SELECTOR = '[data-field-list-container]'
  static PC_FIELD_LIST_UL_SELECTOR = 'ul.field-list'
  static ADD_BUTTON_SELECTOR = '.field-list-add-btn'
  static REMOVE_ALL_BUTTON_SELECTOR = '.field-list-rm-all-btn'
  static REMOVE_BUTTON_SELECTOR = '.field-list-rm-btn'
  static FIELD_ELEMENT_BEARING_VALUE_SELECTOR = '.value-element-form'
  static FIELD_LABEL_SELECTOR = '.label-element-form'
  static EMPTY_TOM_SELECT_FORM_CONTAINER_CLASS = 'empty-tom-select-form-container'
  static PC_FORM_FIELD_CLASS = 'pc-form-field-field'
  static PC_FORM_FIELD_EMPTY_CONTAINER_CLASS = 'pc-form-field-empty-container'

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
      $fieldListContainer.classList.remove('d-none')
    })
  }

  bindEvents = () => {
    this.initialize()
    EventHandler.on(document.body, 'click', PcFieldList.ADD_BUTTON_SELECTOR, this.#onAdd)
    EventHandler.on(document.body, 'click', PcFieldList.REMOVE_BUTTON_SELECTOR, this.#onRemove)
    EventHandler.on(document.body, 'click', PcFieldList.REMOVE_ALL_BUTTON_SELECTOR, this.#onRemoveAll)
  }

  unbindEvents = () => {
    EventHandler.off(document.body, 'click', PcFieldList.ADD_BUTTON_SELECTOR, this.#onAdd)
    EventHandler.off(document.body, 'click', PcFieldList.REMOVE_BUTTON_SELECTOR, this.#onRemove)
    EventHandler.off(document.body, 'click', PcFieldList.REMOVE_ALL_BUTTON_SELECTOR, this.#onRemoveAll)
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

  #generateNextElementNumber = ($ul) => {
    const $$children = $ul.querySelectorAll("li")
    let currentNumber = -1
    if ($$children.length > 0)
    {
        const $lastLi = $$children[$$children.length - 1]
        currentNumber = Number($lastLi.dataset.fieldNumber)
    }
    return currentNumber + 1
  }

  #generateElementName = (originalName, newNumber) => {
    return originalName ? originalName.replace(/^(\w+-)\d+(-\w+)?$/, `$1${newNumber}$2`) : ""
  }

  #filterMaxEntries = ($ul, skipError) => {
    const maxEntries = Number($ul.dataset.maxEntries)
    if (maxEntries && maxEntries !== undefined) {
      const fieldsCount = $ul.children.length
      if (fieldsCount >= maxEntries - 1) {
        this.#changeButtonDisplay($ul, PcFieldList.ADD_BUTTON_SELECTOR, false)
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
      if (fieldsCount <= minEntries) {
        this.#changeButtonDisplay($ul, PcFieldList.REMOVE_BUTTON_SELECTOR, false)
        this.#changeButtonDisplay($ul.parentElement, PcFieldList.REMOVE_ALL_BUTTON_SELECTOR, false)
      }
      if (fieldsCount < minEntries && !skipError) {
        throw new Error('Already min entries');
      }
    }
  }

  #cloneElementFunction = ($ul) => {
    const $firstLi = $ul.firstElementChild
    const { cloneFunctionName } = $firstLi.firstElementChild.dataset
    cloneFunctionName ? this[cloneFunctionName]($ul) : this.#defaultCloneFunction($ul)
  }

  _tomSelectCloneFunction = ($ul) => {
    const tomSelectClass = this.app.addons[this.app.addons.PcTomSelectFieldId.constructor.ID].constructor.PC_TOM_SELECT_FIELD_CLASS
    const $emptyForm = $ul.querySelector(`.${PcFieldList.EMPTY_TOM_SELECT_FORM_CONTAINER_CLASS}`)
    const $removeButton = $ul.querySelector(PcFieldList.REMOVE_BUTTON_SELECTOR).cloneNode(true)
    const $li = document.createElement('li')
    const $newEmptyForm = $emptyForm.cloneNode(true)
    $li.append($newEmptyForm, $emptyForm.cloneNode(true), $removeButton) // we keep a clone within the newly added and edited $newEmptyForm form
    $li.querySelector(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR).classList.add(tomSelectClass)
    this.#resetAndRenameElement($li, this.#generateNextElementNumber($ul))
    $ul.insertBefore($li, $ul.querySelector(PcFieldList.ADD_BUTTON_SELECTOR))
    app.addons.pcTomSelectField.rebindEvents()
    $newEmptyForm.classList.remove("d-none")
    $newEmptyForm.classList.remove(PcFieldList.EMPTY_TOM_SELECT_FORM_CONTAINER_CLASS)
  }

  _formFieldCloneFunction = ($ul) => {
    const $emptyForm = $ul.querySelector(`.${PcFieldList.PC_FORM_FIELD_EMPTY_CONTAINER_CLASS}`)
    const $removeButton = $ul.querySelector(PcFieldList.REMOVE_BUTTON_SELECTOR).cloneNode(true)
    const $li = document.createElement('li')
    $li.classList.add("d-flex", "align-items-start", "justify-content-between", "pt-2")
    const $newEmptyForm = $emptyForm.cloneNode(true)
    $li.append($newEmptyForm, $emptyForm.cloneNode(true), $removeButton) // we keep a clone within the newly added and edited $newEmptyForm form
    // tomSelect code
    const PcTomSelectFieldAddOn = this.app.addons[this.app.addons.PcTomSelectFieldId.constructor.ID].constructor
    const emptyTomSelectClass = PcTomSelectFieldAddOn.EMPTY_PC_TOM_SELECT_FIELD_CONTAINER_CLASS
    const tomSelectClass = this.app.addons[this.app.addons.PcTomSelectFieldId.constructor.ID].constructor.PC_TOM_SELECT_FIELD_CLASS
    $newEmptyForm.classList.remove(PcFieldList.PC_FORM_FIELD_EMPTY_CONTAINER_CLASS)
    const $tomSelectEmptys = $li.getElementsByClassName(emptyTomSelectClass)
    for (let i = 0; i < $tomSelectEmptys.length; i++) {
      const $tomSelectEmpty = $tomSelectEmptys[i]
      if ($tomSelectEmpty.closest(`.${PcFieldList.PC_FORM_FIELD_EMPTY_CONTAINER_CLASS}`)) {
        // ignore tomselect buried in empty form field
        continue
      }
      const $tomSelect = $tomSelectEmpty.previousElementSibling
      const $newTomSelect = $tomSelectEmpty.cloneNode(true)
      $tomSelect.after($newTomSelect)
      $tomSelect.remove()
      $newTomSelect.querySelector("select").classList.add(tomSelectClass)
      $newTomSelect.classList.remove(PcFieldList.EMPTY_TOM_SELECT_FORM_CONTAINER_CLASS)
      $newTomSelect.classList.remove("d-none")
    }
    // end of tomSelect code
    $newEmptyForm.querySelectorAll(".pc-no-update").forEach(($noUpdate) => {
      $noUpdate.classList.remove('pc-no-update')
    })
    this.#resetAndRenameElement($li, this.#generateNextElementNumber($ul))
    $ul.insertBefore($li, $ul.querySelector(PcFieldList.ADD_BUTTON_SELECTOR))

    $newEmptyForm.classList.remove("d-none")
    $newEmptyForm.classList.add(this.app.addons[this.app.addons.PCFormFieldId.constructor.ID].constructor.PC_FORM_FIELD_FIELD_CLASS)
    app.addons.pcTomSelectField.rebindEvents()
    $newEmptyForm.querySelectorAll(this.app.addons[this.app.addons.PCFormFieldId.constructor.ID].constructor.PC_REQUIRED_SELECTOR).forEach(($requiredField) => {
      $requiredField.required = true
    })
    app.addons.pcFormField.rebindEvents()
  }

  #defaultCloneFunction = ($ul) => {
    const firstLi = $ul.firstElementChild
    const $li = firstLi.cloneNode(true)
    this.#resetAndRenameElement($li, this.#generateNextElementNumber($ul))
    $ul.insertBefore($li, $ul.querySelector(PcFieldList.ADD_BUTTON_SELECTOR))
  }


  #resetAndRenameElement = ($li, newNumber) => {
    const { resetAndRenameFunctionName } = $li.firstElementChild.dataset
    $li.dataset.fieldNumber = newNumber
    if (resetAndRenameFunctionName) {
      this[resetAndRenameFunctionName]($li, newNumber)
    } else {
      this.#defaultResetAndRename($li, newNumber)
    }
  }

  _resetAndRenameCheckbox = ($li, newNumber) => {
    $li.querySelectorAll(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR).forEach(($valueElement) => {
      const baseName = $valueElement.dataset.originalName
      const newName = this.#generateElementName(baseName, newNumber)
      $valueElement.id = newName
      $valueElement.name = newName
      $valueElement.checked = $valueElement.dataset.defaultValue
    })
    $li.querySelectorAll(PcFieldList.FIELD_LABEL_SELECTOR).forEach(($labelElement) => {
      const baseName = $labelElement.dataset.originalName
      const newName = this.#generateElementName(baseName, newNumber)
      $labelElement.htmlFor = newName
    })
  }

  #defaultResetAndRename = ($li, newNumber) => {
    $li.querySelectorAll(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR).forEach(($valueElement) => {
      if (!$valueElement.classList.contains('pc-no-update')) {
        const baseName = $valueElement.dataset.originalName
        const newName = this.#generateElementName(baseName, newNumber)
        $valueElement.id = newName
        $valueElement.name = newName
        $valueElement.value = $valueElement.dataset.defaultValue ? $valueElement.dataset.defaultValue : ""
      }
    })
    $li.querySelectorAll(PcFieldList.FIELD_LABEL_SELECTOR).forEach(($labelElement) => {
      if (!$labelElement.classList.contains('pc-no-update')) {
        const baseName = $labelElement.dataset.originalName
        const newName = this.#generateElementName(baseName, newNumber)
        $labelElement.htmlFor = newName

      }
    })
  }

  #getButtonFromEvent = (event) => {
      return event.target.closest('button')
  }

  #onAdd = (event) => {
    const $target = this.#getButtonFromEvent(event)
    const { fieldListContainerId } = $target.dataset
    const $fieldListContainer = this.#getFieldListContainerFromId(fieldListContainerId)
    const $ul = $fieldListContainer.querySelector(PcFieldList.PC_FIELD_LIST_UL_SELECTOR)
    this.#filterMaxEntries($ul)
    this.#cloneElementFunction($ul)
    this.#changeButtonDisplay($ul, PcFieldList.REMOVE_BUTTON_SELECTOR, true)
    this.#changeButtonDisplay($fieldListContainer, PcFieldList.REMOVE_ALL_BUTTON_SELECTOR, true)
  }

  #onRemove = (event) => {
    const $target = this.#getButtonFromEvent(event)
    const { fieldListContainerId } = $target.dataset
    const $fieldListContainer = this.#getFieldListContainerFromId(fieldListContainerId)
    const $ul = $fieldListContainer.querySelector(PcFieldList.PC_FIELD_LIST_UL_SELECTOR)
    const $li = $target.parentElement // remove button is within li
    $li.remove()
    this.#filterMinEntries($ul)
    this.#changeButtonDisplay($ul, PcFieldList.ADD_BUTTON_SELECTOR, true)
  }

  #onRemoveAll = (event) => {
    const $target = this.#getButtonFromEvent(event)
    const $ul = $target.parentElement.querySelector(PcFieldList.PC_FIELD_LIST_UL_SELECTOR)
    const minEntries = Number($ul.dataset.minEntries)
    if (minEntries && minEntries !== undefined) {
      while($ul.children.length > minEntries){
        $ul.lastElementChild.remove()
      }
      for(let i = 0; i < $ul.children.length; i++) {
        const $li = $ul.children[i]
        const fieldNumber = $li.dataset.fieldNumber
        this.#resetAndRenameElement($li, fieldNumber)
      }
    }
    this.#filterMinEntries($ul, false)
  }

}
