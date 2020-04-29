import React from 'react'
import { Field } from 'react-final-form'
import formatSiren from './formatSiren'
import { composeValidators, removeWhitespaces } from 'react-final-form-utils'
import { getSirenInformation } from '../../../../pages/Offerer/OffererCreation/decorators/getSirenInformation'
import FieldErrors from '../../FieldErrors'
import PropTypes from 'prop-types'

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

const SirenField = props => (
  <Field
    format={formatSiren}
    minLength={11}
    name="siren"
    validate={composeValidators(required, mustHaveTheProperLength, existsInINSEERegistry)}
  >
    {({ input, meta }) => {
      return (
        <label className="field-siren">
          <span className="field-siren-label">
            {'SIREN'}
            <span className="field-asterisk">
              {'*'}
            </span>
          </span>

          {props.subLabel && <span className="sub-label">
            {props.subLabel}
                             </span>}

          <div className="field-siren-control">
            <span className="field-siren-input-value">
              <input
                {...input}
                className="input"
                placeholder="123 456 789"
                required
                type="text"
              />

              {props.value && <span className="field-siren-value">
                {props.value}
                              </span>}
            </span>

            <FieldErrors
              className="field-siren-error"
              meta={meta}
            />
          </div>
        </label>
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
