/* eslint
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames'
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'
import { composeValidators } from 'react-final-form-utils'

import Address from './Address'
import FieldErrors from 'components/layout/form/FieldErrors'
import validateRequiredField from 'components/layout/form/utils/validateRequiredField'

const createBatchGeoChanges = form => values => {
  form.batch(() => {
    const {
      address,
      city,
      latitude,
      longitude,
      postalCode,
      selectedAddress,
    } = values
    form.change('address', address)
    form.change('city', city)
    form.change('latitude', latitude)
    form.change('longitude', longitude)
    form.change('postalCode', postalCode)
    form.change('selectedAddress', selectedAddress)
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
}) => {
  const requiredValidate =
    required && typeof required === 'function'
      ? required
      : (required && validateRequiredField) || undefined

  const batchGeoChanges = createBatchGeoChanges(form)

  return (
    <Field
      format={format}
      name={name}
      validate={composeValidators(validate, requiredValidate)}
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
                  <Address
                    {...input}
                    {...AddressProps}
                    className="field-input field-address"
                    disabled={disabled || readOnly}
                    name={name}
                    onMarkerDragend={batchGeoChanges}
                    onSuggestionSelect={batchGeoChanges}
                    onTextChange={batchGeoChanges}
                    placeholder={readOnly ? '' : placeholder}
                    readOnly={readOnly}
                    required={!!required}
                  />
                  {renderInner()}
                </div>
                {renderValue()}
              </div>
              <FieldErrors meta={meta} />
            </div>
            <div />
          </div>
        )
      }}
    />
  )
}

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
  renderInner: () => null,
  renderValue: () => null,
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
