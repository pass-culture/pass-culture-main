import * as yup from 'yup'

import { TextInput } from 'ui-kit'

const identityFormFields = [
  <TextInput label="Prénom" name="firstName" />,
  <TextInput label="Nom" name="lastName" />,
]

const identityFormValidationSchema = yup.object().shape({
  firstName: yup.string().max(128).required(),
  lastName: yup.string().max(128).required(),
})

export const userProfileForms = [
  {
    fields: identityFormFields,
    schema: identityFormValidationSchema,
  },
]
