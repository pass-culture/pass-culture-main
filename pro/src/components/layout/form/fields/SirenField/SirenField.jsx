import PropTypes from 'prop-types'
import React from 'react'
import { Field } from 'react-final-form'
import { removeWhitespaces } from 'react-final-form-utils'

import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { getSirenInformation } from 'repository/siren/getSirenInformation'
import { composeValidators } from 'utils/react-final-form'

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
  if (sirenInformation.error === 'SIREN invalide')
    return "Ce SIREN n'est pas reconnu"
  if (sirenInformation.error === 'Service indisponible')
    return 'L’Annuaire public des Entreprises est indisponible. Veuillez réessayer plus tard.'
  return undefined
})

const SirenField = ({ label }) => (
  <Field
    format={formatSiren}
    minLength={11}
    name="siren"
    validate={composeValidators(
      required,
      mustHaveTheProperLength,
      existsInINSEERegistry
    )}
  >
    {({ input, meta }) => {
      return (
        <TextInput
          error={meta.modified && meta.error ? meta.error : null}
          label={label}
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

SirenField.defaultProps = {
  label: 'SIREN',
}

SirenField.propTypes = {
  label: PropTypes.string,
}

export default SirenField
