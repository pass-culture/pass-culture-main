import React, { Fragment } from 'react'
import { Field } from 'react-final-form'
import formatSiren from './formatSiren'
import { composeValidators, removeWhitespaces } from 'react-final-form-utils'
import { getSirenInformation } from '../../../../pages/Offerer/OffererCreation/decorators/getSirenInformation'
import PropTypes from 'prop-types'
import TextInput from '../../../inputs/TextInput/TextInput'

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
          <Fragment>
            <TextInput
              {...input}
              error={meta.modified && meta.error ? meta.error : null}
              label="SIREN"
              maxLength="11"
              name="siren"
              placeholder="123 456 789"
              sublabel="obligatoire"
            />
          </Fragment>
        )
      }}
    </Field>
  )

SirenField.defaultProps = {
  subLabel: null,
  value: null,
}

SirenField.propTypes = {
  subLabel: PropTypes.string,
  value: PropTypes.string,
}

export default SirenField
