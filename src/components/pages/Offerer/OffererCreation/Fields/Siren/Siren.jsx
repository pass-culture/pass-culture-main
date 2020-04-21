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
        <label className="field text-field is-label-aligned op-field">
          <span className="field-label" htmlFor="offerer__siren">
            {'SIREN : '}
            <span className="field-asterisk">{'*'}</span>
          </span>
          <div className="field-control">
            <div className="field-value flex-columns items-center">
              <div className="field-inner flex-columns items-center">
                <input className="input is-normal" id="offerer__siren" type="text" {...input} />
              </div>
            </div>
            <FieldErrors meta={meta} />
          </div>
        </label>
      )
    }}
  </Field>
)

export default Siren
