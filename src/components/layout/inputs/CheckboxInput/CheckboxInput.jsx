import PropTypes from 'prop-types'
import React from 'react'

export const CheckboxInput = ({
  onChange,
  name,
  label,
  checked,
  isInError,
  labelAttributes,
  className,
  hiddenLabel,
  subLabel,
  SvgElement,
  ...attributes
}) => {
  let labelClasses = ['field', 'field-checkbox']
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
          <span className="ic-sub-label">
            {subLabel}
          </span>
        )}
      </span>
    </label>
  )
}

CheckboxInput.defaultProps = {
  SvgElement: null,
  className: '',
  hiddenLabel: false,
  isInError: false,
  labelAttributes: {},
  subLabel: null,
}

CheckboxInput.propTypes = {
  SvgElement: PropTypes.elementType,
  checked: PropTypes.bool.isRequired,
  className: PropTypes.string,
  hiddenLabel: PropTypes.bool,
  isInError: PropTypes.bool,
  label: PropTypes.string.isRequired,
  labelAttributes: PropTypes.shape(),
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  subLabel: PropTypes.string,
}
