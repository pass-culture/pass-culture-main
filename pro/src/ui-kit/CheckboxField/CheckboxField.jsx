import cx from 'classnames'
import PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import { Field } from 'react-final-form'

import getRequiredValidate from 'components/layout/form/utils/getRequiredValidate'

const CheckboxField = ({
  SvgElement,
  className,
  disabled,
  id,
  label,
  labelAligned,
  name,
  required,
}) => {
  const renderCheckbox = useCallback(
    inputProps => {
      return (
        <label className={cx('checkbox-field', className)} htmlFor={id}>
          <input {...inputProps} id={id} type="checkbox" />
          {SvgElement && <SvgElement aria-hidden />}
          <span className="input-checkbox-label">{label}</span>
        </label>
      )
    },
    [SvgElement, className, id, label]
  )

  const renderLabelAlignedField = useCallback(
    inputProps => (
      <div className="field is-label-aligned">
        <div className="field-label" />
        <div className="field-control">{renderCheckbox(inputProps)}</div>
      </div>
    ),
    [renderCheckbox]
  )

  const renderField = useCallback(
    ({ input }) => {
      let inputProps = { ...input }

      if (disabled) {
        inputProps.disabled = disabled
      }

      if (labelAligned) {
        return renderLabelAlignedField(inputProps)
      }

      return renderCheckbox(inputProps)
    },
    [disabled, labelAligned, renderCheckbox, renderLabelAlignedField]
  )

  return (
    <Field
      name={name}
      render={renderField}
      type="checkbox"
      validate={getRequiredValidate(required, 'boolean')}
    />
  )
}

CheckboxField.defaultProps = {
  SvgElement: null,
  className: '',
  disabled: false,
  label: '',
  labelAligned: false,
  required: false,
}

CheckboxField.propTypes = {
  SvgElement: PropTypes.elementType,
  className: PropTypes.string,
  disabled: PropTypes.bool,
  id: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelAligned: PropTypes.bool,
  name: PropTypes.string.isRequired,
  required: PropTypes.bool,
}

export default CheckboxField
