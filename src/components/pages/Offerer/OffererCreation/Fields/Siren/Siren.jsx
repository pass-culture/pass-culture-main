import React from 'react'
import { Field } from 'react-final-form'
import FieldErrors from '../../../../../layout/form/FieldErrors'
import formatSiren from './formatSiren'
import { composeValidators, removeWhitespaces } from 'react-final-form-utils'
import getSirenInformation from '../../decorators/getSirenInformation'

const required = value => {
  return value ? undefined : 'Ce champs est obligatoire'
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

const Siren = () => (
  <Field
    format={formatSiren}
    minLength={11}
    name="siren"
    validate={composeValidators(required, mustHaveTheProperLength, existsInINSEERegistry)}
  >
    {({ input, meta }) => {
      return (
        <label className="op-field-siren">
          <span className="op-field-label-siren">
            {'SIREN : '}
            <span className="field-asterisk">
              {'*'}
            </span>
          </span>
          <div className="op-field-control-siren">
            <input
              className="input"
              id="offerer__siren"
              type="text"
              {...input}
            />
            <FieldErrors
              className="op-field-error-siren"
              meta={meta}
            />
          </div>
        </label>
      )
    }}
  </Field>
)

export default Siren
