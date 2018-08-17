const submitForm = formid => {
  // NOTE -> soumission du form depuis un element exterieur au form
  const event = new Event('submit')
  document.getElementById(formid).dispatchEvent(event)
}

export default submitForm
