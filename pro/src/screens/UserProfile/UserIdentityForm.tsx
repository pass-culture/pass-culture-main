import * as yup from 'yup'

import FormLayout from 'new_components/FormLayout'
import React from 'react'
import { TextInput } from 'ui-kit'

export const identityFormFields = [
  <>
    <FormLayout.Row>
      <TextInput label="Prénom" name="firstName" />,
    </FormLayout.Row>
    <FormLayout.Row>
      <TextInput label="Nom" name="lastName" />
    </FormLayout.Row>
  </>,
]

export const identityFormSchema = yup.object().shape({
  firstName: yup.string().max(128).required(),
  lastName: yup.string().max(128).required(),
})
