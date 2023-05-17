/**
 * This adds PcAddOn support for field list (PcFieldList).
 */
class PcFieldList extends PcAddOn {

  static PC_FIELD_LIST_CONTAINER = '.field-list'
  static ADD_BUTTON_SELECTOR = '.field-list-add-btn'
  static REMOVE_BUTTON_SELECTOR = '.field-list-rm-btn'
  static FIELD_ELEMENT_BEARING_VALUE_SELECTOR = '.value-element-form'
  static FIELD_LABEL_SELECTOR = '.label-element-form'

  get $$addButton() {
    return document.querySelectorAll(PcFieldList.ADD_BUTTON_SELECTOR)
  }
  get $$removeButton() {
    return document.querySelectorAll(PcFieldList.REMOVE_BUTTON_SELECTOR)
  }

  get $$fieldList() {
    return document.querySelectorAll(PcFieldList.PC_FIELD_LIST_CONTAINER)
  }

  getTagFromEvent = (event, tag) => {
    let candidate = event.target;
    while (candidate.tagName !== tag) {
      candidate = candidate.parentNode
      if (candidate.tagName === "BODY") {
        throw new Error('Pas trouvé de ' + tag + ' !')
      }
    }
    return candidate
  }

  changeButtonDisplay = (ulElement, selector, display) => {
    const buttons = ulElement.querySelectorAll(selector)
    for (let i = 0; i < buttons.length; i++) {
      buttons[i].style.display = display
    }
  }

  generateNextElementName = (ulElement) => {
    const baseFieldName = ulElement.dataset.fieldName
    const nextFieldNumber = Number(ulElement.dataset.entriesCount)
    ulElement.dataset.entriesCount = nextFieldNumber + 1
    return baseFieldName + "-" + nextFieldNumber
  }

  filterMaxEntries = (ulElement, silent) => {
    if (ulElement.dataset.maxEntries && ulElement.dataset.maxEntries != undefined) {
      const fieldsCount = ulElement.children.length - 1
      const maxEntries = Number(ulElement.dataset.maxEntries)
      if (fieldsCount >= maxEntries - 1) {
        this.changeButtonDisplay(ulElement, PcFieldList.ADD_BUTTON_SELECTOR, "none")
      }
      if (fieldsCount >= maxEntries && !silent) {
        throw new Error('Already max entries');
      }
    }
  }

  filterMinEntries = (ulElement, silent) => {
    if (ulElement.dataset.minEntries && ulElement.dataset.minEntries != undefined) {
      const fieldsCount = ulElement.children.length - 1
      const minEntries = Number(ulElement.dataset.minEntries)
      if (fieldsCount <= minEntries + 1) {
        this.changeButtonDisplay(ulElement, PcFieldList.REMOVE_BUTTON_SELECTOR, "none")
      }
      if (fieldsCount <= minEntries && !silent) {
        throw new Error('Already min entries');
      }
    }
  }


  cloneElementFunction = (ulElement) => {
    const firstLi = ulElement.firstElementChild
    const cloneFunctionName = firstLi.firstElementChild.dataset.cloneFunction
    if (cloneFunctionName) {
      this[cloneFunctionName](ulElement)
    } else {
      this.defaultCloneFunction(ulElement)
    }
  }
  // clone functions --------------------------------------------------------------
  tomSelectCloneFunction = (ulElement) => {
    const emptyForm = ulElement.querySelector(".empty-tom-select-form")

    const newIlElement = document.createElement("li")
    const newNodeDivContainer = emptyForm.cloneNode(true)
    newIlElement.appendChild(newNodeDivContainer)
    newIlElement.appendChild(emptyForm.cloneNode(true))
    newIlElement.appendChild(ulElement.querySelector(PcFieldList.REMOVE_BUTTON_SELECTOR).cloneNode(true))
    const newNodeClassList = newIlElement.querySelector(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR).classList.add("pc-tom-select-field")

    const newName = this.generateNextElementName(ulElement)
    this.resetAndRenameElement(newIlElement, newName)

    ulElement.insertBefore(newIlElement, ulElement.querySelector(PcFieldList.ADD_BUTTON_SELECTOR))
    newIlElement.querySelector(PcFieldList.REMOVE_BUTTON_SELECTOR).addEventListener("click", this.rmButtonFieldList)
    app.addons.pcTomSelectField.bindEvents()
    newNodeDivContainer.classList.remove("d-none")
    newNodeDivContainer.classList.remove("empty-tom-select-form")
  }

  defaultCloneFunction = (ulElement) => {
    const firstLi = ulElement.firstElementChild
    const newIlElement = firstLi.cloneNode(true)
    const newName = this.generateNextElementName(ulElement)
    this.resetAndRenameElement(newIlElement, newName)
    ulElement.insertBefore(newIlElement, ulElement.querySelector(PcFieldList.ADD_BUTTON_SELECTOR))
    newIlElement.querySelector(PcFieldList.REMOVE_BUTTON_SELECTOR).addEventListener("click", this.rmButtonFieldList)
  }
  // /clone functions -------------------------------------------------------------

  resetAndRenameElement = (newIlElement, newName) => {
    const resetAndRenameFunctionName = newIlElement.firstElementChild.dataset.resetAndRenameFunction
    if (resetAndRenameFunctionName) {
      this[resetAndRenameFunctionName](newIlElement, newName)
    } else {
      this.defaultResetAndRename(newIlElement, newName)
    }
  }

  // reset functions --------------------------------------------------------------
  resetAndRenameCheckbox = (newIlElement, newName) => {
    const valueElement = newIlElement.querySelector(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR)
    const label = newIlElement.querySelector(PcFieldList.FIELD_LABEL_SELECTOR)
    valueElement.id = newName
    valueElement.name = newName
    valueElement.checked = valueElement.dataset.defaultValue
    if (label != null) {
      label.htmlFor = newName
    }
  }

  defaultResetAndRename = (newIlElement, newName) => {
    const valueElement = newIlElement.querySelector(PcFieldList.FIELD_ELEMENT_BEARING_VALUE_SELECTOR)
    const label = newIlElement.querySelector(PcFieldList.FIELD_LABEL_SELECTOR)
    valueElement.id = newName
    valueElement.name = newName
    valueElement.value = valueElement.dataset.defaultValue ? valueElement.dataset.defaultValue : ""
    if (label != null) {
      label.htmlFor = newName
    }
  }

  addButtonFieldList = (event) => {
    const ulElement = this.getTagFromEvent(event, "UL")
    this.filterMaxEntries(ulElement)
    const newIlElement = this.cloneElementFunction(ulElement)
    this.changeButtonDisplay(ulElement, PcFieldList.REMOVE_BUTTON_SELECTOR, "")
  }

  rmButtonFieldList = (event) => {
    const ulElement = this.getTagFromEvent(event, "UL")
    const liElement = this.getTagFromEvent(event, "LI")
    this.filterMinEntries(ulElement)
    liElement.querySelector(PcFieldList.REMOVE_BUTTON_SELECTOR).removeEventListener("click", this.rmButtonFieldList)
    liElement.remove()
    this.changeButtonDisplay(ulElement, PcFieldList.ADD_BUTTON_SELECTOR, "")
  }

  bindEvents = () => {
    if(this.$$fieldList)
    {
      this.$$addButton.forEach((button) => {button.addEventListener("click", this.addButtonFieldList)})
      this.$$removeButton.forEach((button) => {button.addEventListener("click", this.rmButtonFieldList)})

      this.$$fieldList.forEach((fieldList) => {
          this.filterMaxEntries(fieldList, true)
          this.filterMinEntries(fieldList, true)
        }
      )
    }
  }

  unbindEvents = () => {
    if(this.$$fieldList)
    {
      this.$$addButton.forEach((button) => {button.removeEventListener("click", this.addButtonFieldList)})
      this.$$removeButton.forEach((button) => {button.removeEventListener("click", this.rmButtonFieldList)})
    }
  }
}
