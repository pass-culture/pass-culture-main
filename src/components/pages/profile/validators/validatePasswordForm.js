/**
 * USER PROFILE PAGE
 * Fichier de validation du formulaire du changement de mot de passe
 */
import { FORM_ERROR } from 'final-form'
import isEqual from 'lodash.isequal'

import { isPassword } from '../../../../utils/strings'

const DEFAULT_REQUIRED_ERROR = 'Ce champs est requis.'
const ERROR_IS_NOT_MATCHING_CONFIRM =
  'Les deux mots de passe ne sont pas identiques.'
const ERROR_IS_EQUAL_ORIGINAL =
  'Votre nouveau mot de passe doit être différent de votre ancien mot de passe.'

const validateEqualities = values => {
  const isMatchingOriginal =
    values.newPassword &&
    values.oldPassword &&
    isEqual(values.newPassword, values.oldPassword)
  // si le nouveau mot de passe correspond à l'ancien
  if (isMatchingOriginal) {
    return { [FORM_ERROR]: ERROR_IS_EQUAL_ORIGINAL }
  }
  const isMatchingConfirm =
    values.newPassword &&
    values.newPasswordConfirm &&
    isEqual(values.newPassword, values.newPasswordConfirm)
  // si le nouveau mot de passe ne correspond pas à la confirmation
  if (!isMatchingConfirm) {
    return { [FORM_ERROR]: ERROR_IS_NOT_MATCHING_CONFIRM }
  }
  return {}
}

// On verifie pas que le champs oldPassword est du type password
// On verifie juste qu'il n'est pas vide
const FORM_KEYS = ['newPassword', 'newPasswordConfirm']
// const FORM_KEYS = ['oldPassword', 'newPassword', 'newPasswordConfirm']
const validatePasswordForm = formValues => {
  let errors = FORM_KEYS.reduce((acc, key) => {
    const value = formValues[key]
    if (!isPassword(value)) return { ...acc, [key]: DEFAULT_REQUIRED_ERROR }
    return acc
  }, {})
  const hasErrors = Object.keys(errors).length > 0
  // si pas d'erreurs on vérifie les égalités des champs
  if (!hasErrors) errors = validateEqualities(formValues)
  return errors
}

export default validatePasswordForm
