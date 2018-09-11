// soumission du form depuis un element exterieur au form
const submitForm = formid => {
  // NOTE -> submit form form extenal button will reload the page in firefox
  // SEE -> https://github.com/facebook/react/issues/12639
  const opts = { cancelable: true }
  const event = new Event('submit', opts)
  document.getElementById(formid).dispatchEvent(event)
}

export default submitForm
