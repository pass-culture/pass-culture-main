import React from 'react'
import { Field } from 'react-final-form'
import { composeValidators, removeWhitespaces } from 'react-final-form-utils'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { getSirenInformation } from 'components/pages/Offerer/OffererCreation/decorators/getSirenInformation'

import formatSiren from './formatSiren'

const required = value => {
  return value ? undefined : 'Ce champ est obligatoire'
}

const mustHaveTheProperLength = value => {
  return value.length < 11 ? 'SIREN trop court' : undefined
}

export const existsInINSEERegistry = async value => {
  value = removeWhitespaces(value)
  const sirenInformation = await getSirenInformation(value)
  if (sirenInformation.error) return "Ce SIREN n'est pas reconnu"
  return undefined
}

const SirenField = () => (
  <Field
    format={formatSiren}
    minLength={11}
    name="siren"
    validate={composeValidators(required, mustHaveTheProperLength, existsInINSEERegistry)}
  >
    {({ input, meta }) => {
      return (
        <TextInput
          error={meta.modified && meta.error ? meta.error : null}
          label="SIREN"
          maxLength="11"
          name="siren"
          onChange={input.onChange}
          placeholder="123 456 789"
          sublabel="obligatoire"
          value={input.value}
        />
      )
    }}
  </Field>
)

export default SirenField
