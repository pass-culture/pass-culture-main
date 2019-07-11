// soumission du form depuis un element exterieur au form
export const externalSubmitForm = formid => () => {
  // NOTE -> submit form from external button will reload the page in firefox
  // SEE -> https://github.com/facebook/react/issues/12639
  const opts = { cancelable: true }
  const event = new Event('submit', opts)
  const formElement = document.getElementById(formid)
  if (formElement) {
    formElement.dispatchEvent(event)
  }
}

export default externalSubmitForm
