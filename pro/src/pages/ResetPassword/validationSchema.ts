import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  newPassword: yup
    .string()
    .required('Veuillez renseigner votre nouveau mot de passe'),

  // Adds "newConfirmationPassword" validation
  newConfirmationPassword: yup
    .string()
    .oneOf(
      [yup.ref('newPassword')],
      'Vos nouveaux mots de passe ne correspondent pas'
    )
    .required('Veuillez confirmer votre nouveau mot de passe'),
})
