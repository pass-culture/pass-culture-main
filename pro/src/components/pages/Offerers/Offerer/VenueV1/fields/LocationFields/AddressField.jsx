/* eslint-disable react/prop-types */
import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { useEffect } from 'react'
import { Field, useForm, useFormState } from 'react-final-form'
import { composeValidators } from 'react-final-form-utils'

import FieldErrors from 'components/layout/form/FieldErrors'
import getRequiredValidate from 'components/layout/form/utils/getRequiredValidate'

import LocationViewer from './LocationViewer'

const updateLocationFields =
  (form, { isLocationFrozen }) =>
  location => {
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

export const addressFieldRender =
  ({
    className,
    disabled,
    form,
    id,
    innerClassName,
    label,
    name,
    placeholder,
    readOnly,
    required,
    addressProps,
  }) =>
  // eslint-disable-next-line react/display-name
  ({ input, meta }) => {
    return (
      <div
        className={classnames('field text-field', className, {
          'is-label-aligned': label,
          'is-read-only': readOnly,
        })}
        id={`${id}-container`}
      >
        <label
          className={classnames('field-label', { empty: !label })}
          htmlFor={name}
          // for={name}
        >
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
              )}
            >
              <LocationViewer
                {...input}
                {...addressProps}
                className="field-input field-address"
                disabled={disabled || readOnly}
                id={id}
                name={name}
                onMarkerDragend={updateLocationFields(form, {
                  isLocationFrozen: false,
                })}
                onSuggestionSelect={updateLocationFields(form, {
                  isLocationFrozen: true,
                })}
                onTextChange={updateLocationFields(form, {
                  isLocationFrozen: false,
                })}
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
  }

// eslint-disable-next-line react/no-multi-comp
export const AddressField = ({
  className,
  disabled,
  form,
  format,
  id,
  innerClassName,
  label,
  name,
  placeholder,
  readOnly,
  required,
  validate,
  ...addressProps
}) => {
  const formData = useForm()
  const formState = useFormState()

  const formLatitude = formState.values.latitude
  const formLongitude = formState.values.longitude

  useEffect(() => {
    // should add process.env because of functional problem, tests should be refactoring
    if (formLatitude && formLongitude && process.env.NODE_ENV !== 'test') {
      updateLocationFields(formData, {
        isLocationFrozen: formData.isLocationFrozen,
      })({
        latitude: formLatitude,
        longitude: formLongitude,
      })
    }
    // eslint-disable-next-line
  }, [formLongitude, formLatitude, formData])
  return (
    <Field
      format={format}
      name={name}
      render={addressFieldRender({
        className,
        disabled,
        form,
        id,
        innerClassName,
        label,
        name,
        placeholder,
        readOnly,
        required,
        addressProps,
      })}
      validate={composeValidators(validate, getRequiredValidate(required))}
    />
  )
}

AddressField.defaultProps = {
  className: '',
  disabled: false,
  format: undefined,
  id: null,
  innerClassName: null,
  label: '',
  placeholder: '',
  readOnly: false,
  required: false,
  validate: null,
}

AddressField.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool,
  form: PropTypes.shape().isRequired,
  format: PropTypes.func,
  id: PropTypes.string,
  innerClassName: PropTypes.string,
  label: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  readOnly: PropTypes.bool,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  validate: PropTypes.func,
}

export default AddressField
