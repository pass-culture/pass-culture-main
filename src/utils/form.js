import get from 'lodash.get'
import { DELETE } from './config'

export function getElementsWithoutDeletedFormValues (dataElements, formElements) {
  // init
  const elements = []

  // remove the dataElements that was deleted inside the form
  // and add the new created ones
  for (let dataElement of (dataElements || [])) {
    const index = formElements.findIndex(formElement =>
      (formElement && formElement.id) === dataElement.id)
    if (index > -1) {
      const formElement = formElements[index]
      if (formElement.DELETE === DELETE) {
        delete formElements[index]
      } else {
        elements.push(formElement)
      }
    } else {
      elements.push(dataElement)
    }
  }

  // add the new ones
  formElements.forEach(formElement =>
    elements.push(formElement))

  // return
  return elements
}

export function getIsDisabled (form, keys, isNew) {
  return !form || isNew
    ? keys.filter(f => !get(form, f)).length > 0
    : keys.every(f => !get(form, f))
}
