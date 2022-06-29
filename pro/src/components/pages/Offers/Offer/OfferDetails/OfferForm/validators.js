import {
  DEFAULT_FORM_VALUES,
  WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE,
} from '../_constants'

export const isUrlValid = val => {
  /*eslint-disable-next-line no-useless-escape*/
  const urlRegex = new RegExp(
    /^(http|https):\/\/([A-z0-9-_]+)\.([A-z0-9-_]{2,})/
  )
  if (val === null || val === '') {
    return true
  }
  return urlRegex.test(val)
}

export const isFormValid = (formValues, offerFormFields, mandatoryFields) => {
  let errors = {}
  const formFields = [...offerFormFields, 'offererId']

  mandatoryFields.forEach(fieldName => {
    if (
      formFields.includes(fieldName) &&
      formValues[fieldName] === DEFAULT_FORM_VALUES[fieldName]
    ) {
      errors[fieldName] = 'Ce champ est obligatoire.'
    }
  })

  if (
    ![
      formValues.noDisabilityCompliant,
      formValues.audioDisabilityCompliant,
      formValues.mentalDisabilityCompliant,
      formValues.motorDisabilityCompliant,
      formValues.visualDisabilityCompliant,
    ].includes(true)
  ) {
    errors['disabilityCompliant'] = 'Ce champ est obligatoire.'
  }

  if (!isUrlValid(formValues.url)) {
    errors['url'] = 'Veuillez renseigner une URL valide'
  }

  if (!isUrlValid(formValues.externalTicketOfficeUrl)) {
    errors['externalTicketOfficeUrl'] = 'Veuillez renseigner une URL valide'
  }

  if (
    WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(
      formValues.subcategoryId
    ) &&
    !formValues.withdrawalType
  ) {
    errors['withdrawalType'] = `Vous devez cocher l'une des options ci-dessus`
  }

  return errors
}
