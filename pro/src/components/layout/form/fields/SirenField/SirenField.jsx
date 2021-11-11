/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt deprecated "Gaël: deprecated usage of react-final-form"
*/

import React from 'react'
import { Field } from 'react-final-form'
import { composeValidators, removeWhitespaces } from 'react-final-form-utils'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { getSirenInformation } from 'repository/siren/getSirenInformation'

import formatSiren from './formatSiren'

const required = value => {
  return value ? undefined : 'Ce champ est obligatoire'
}

const mustHaveTheProperLength = value => {
  return value.length < 9 ? 'SIREN trop court' : undefined
}

const simpleMemoize = fn => {
  let lastArg
  let lastResult
  return arg => {
    if (arg !== lastArg) {
      lastArg = arg
      lastResult = fn(arg)
    }
    return lastResult
  }
}

export const existsInINSEERegistry = simpleMemoize(async value => {
  value = removeWhitespaces(value)
  const sirenInformation = await getSirenInformation(value)
  if (sirenInformation.error) return "Ce SIREN n'est pas reconnu"
  return undefined
})

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
          placeholder="123456789"
          sublabel="obligatoire"
          value={input.value}
        />
      )
    }}
  </Field>
)

export default SirenField
