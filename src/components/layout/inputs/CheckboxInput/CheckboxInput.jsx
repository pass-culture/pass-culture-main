import PropTypes from 'prop-types'
import React from 'react'

export const CheckboxInput = ({
  onChange,
  name,
  label,
  checked,
  isInError,
  isLabelDisable,
  labelAttributes,
  className,
  hiddenLabel,
  subLabel,
  SvgElement,
  ...attributes
}) => {
  let labelClasses = ['field', 'field-checkbox']
  let subLabelClasses = ['ic-sub-label']
  if (isLabelDisable) {
    labelClasses.push('disabled')
    subLabelClasses.push('disabled')
  }
  if (isInError) {
    labelClasses.push('error')
  }
  let inputClasses = className ? className.split(' ') : []
  let textClasses = ['input-checkbox-label']
  if (hiddenLabel) {
    textClasses.push('label-hidden')
  }
  inputClasses.push('input-checkbox-input')

  return (
    <label
      className={labelClasses.join(' ')}
      {...labelAttributes}
    >
      <input
        checked={checked}
        className={inputClasses.join(' ')}
        name={name}
        onChange={onChange}
        type="checkbox"
        {...attributes}
      />
      {SvgElement && <SvgElement aria-hidden />}
      <span className={textClasses.join(' ')}>
        {label}
        {subLabel && (
          <span className={subLabelClasses.join(' ')}>
            {subLabel}
          </span>
        )}
      </span>
    </label>
  )
}

CheckboxInput.defaultProps = {
  SvgElement: null,
  checked: false,
  className: '',
  hiddenLabel: false,
  isInError: false,
  isLabelDisable: false,
  labelAttributes: {},
  subLabel: null,
}

CheckboxInput.propTypes = {
  SvgElement: PropTypes.elementType,
  checked: PropTypes.bool,
  className: PropTypes.string,
  hiddenLabel: PropTypes.bool,
  isInError: PropTypes.bool,
  isLabelDisable: PropTypes.bool,
  label: PropTypes.string.isRequired,
  labelAttributes: PropTypes.shape(),
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  subLabel: PropTypes.string,
}
