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
        <div className="field text-field is-label-aligned">
          <label
            className="field-label"
            htmlFor="offerer__siren"
          >
            <span>
              {'SIREN : '}
            </span>
            <span className="field-asterisk">
              {'*'}
            </span>
          </label>
          <div className="field-control">
            <div className="field-value flex-columns items-center">
              <div className="field-inner flex-columns items-center">
                <input
                  className="input is-normal"
                  id="offerer__siren"
                  type="text"
                  {...input}
                />
              </div>
            </div>
            <FieldErrors meta={meta} />
          </div>
        </div>
      )
    }}
  </Field>
)

export default Siren
