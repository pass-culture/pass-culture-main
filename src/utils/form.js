import { DELETE } from './config'

export function getElementsWithoutDeletedFormValues (dataElements, formElements) {
  // init
  const elements = []

  // remove the dataElements that was deleted inside the form
  // and add the new created ones
  console.log('dataElement', dataElements, formElements)
  for (let dataElement of dataElements) {
    const index = formElements.findIndex(formElement =>
      (formElement && formElement.id) === dataElement.id)
    console.log('formElements', formElements)
    console.log('index', index)
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

  console.log('elements', elements)
  // return
  return elements
}
