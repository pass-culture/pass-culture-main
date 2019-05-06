/* eslint
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames'
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'
import { composeValidators } from 'react-final-form-utils'

import LocationViewer from './LocationViewer'
import FieldErrors from 'components/layout/form/FieldErrors'
import getRequiredValidate from 'components/layout/form/utils/getRequiredValidate'

const createBatchLocationChanges = (form, isLocationFrozen) => location => {
  form.batch(() => {
    const { address, city, latitude, longitude, postalCode } = location
    form.change('address', address)
    form.change('city', city)
    form.change('isLocationFrozen', isLocationFrozen)
    form.change('latitude', latitude)
    form.change('longitude', longitude)
    form.change('postalCode', postalCode)
  })
}

export const AddressField = ({
  className,
  disabled,
  form,
  format,
  id,
  innerClassName,
  label,
  name,
  parse,
  placeholder,
  readOnly,
  renderInner,
  renderValue,
  required,
  validate,
  ...AddressProps
}) => (
  <Field
    format={format}
    name={name}
    validate={composeValidators(validate, getRequiredValidate(required))}
    render={({ input, meta }) => {
      return (
        <div
          className={classnames('field text-field', className, {
            'is-label-aligned': label,
            'is-read-only': readOnly,
          })}
          id={id}>
          <label
            htmlFor={name}
            className={classnames('field-label', { empty: !label })}>
            {label && (
              <span>
                <span>{label}</span>
                {required && !readOnly && (
                  <span className="field-asterisk">*</span>
                )}
              </span>
            )}
          </label>
          <div className="field-control">
            <div className="field-value flex-columns items-center">
              <div
                className={classnames(
                  'field-inner flex-columns items-center',
                  innerClassName
                )}>
                <LocationViewer
                  {...input}
                  {...AddressProps}
                  className="field-input field-address"
                  disabled={disabled || readOnly}
                  name={name}
                  onMarkerDragend={createBatchLocationChanges(form, false)}
                  onSuggestionSelect={createBatchLocationChanges(form, true)}
                  onTextChange={createBatchLocationChanges(form, false)}
                  placeholder={readOnly ? '' : placeholder}
                  readOnly={readOnly}
                  required={!!required}
                />
              </div>
            </div>
            <FieldErrors meta={meta} />
          </div>
          <div />
        </div>
      )
    }}
  />
)

AddressField.defaultProps = {
  className: '',
  disabled: false,
  format: null,
  id: null,
  innerClassName: null,
  label: '',
  parse: null,
  placeholder: '',
  readOnly: false,
  required: false,
  type: 'text',
  validate: null,
}

AddressField.propTypes = {
  autoComplete: PropTypes.string,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  form: PropTypes.object.isRequired,
  format: PropTypes.func,
  id: PropTypes.string,
  innerClassName: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  parse: PropTypes.func,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  renderInner: PropTypes.func,
  renderValue: PropTypes.func,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  validate: PropTypes.func,
}

export default AddressField
