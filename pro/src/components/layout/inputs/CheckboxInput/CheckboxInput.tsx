import React from 'react'

interface IProps {
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void
  label: string
  name: string
  SvgElement?: React.ComponentType | null
  checked?: boolean
  className?: string
  disabled?: boolean
  hiddenLabel?: boolean
  isInError?: boolean
  isLabelDisable?: boolean
  subLabel?: string | null
}

const CheckboxInput = ({
  SvgElement = null,
  checked = false,
  className = '',
  disabled = false,
  hiddenLabel = false,
  isInError = false,
  isLabelDisable = false,
  label,
  name,
  onChange,
  subLabel = null,
}: IProps): JSX.Element => {
  const labelClasses = ['field', 'field-checkbox']
  const subLabelClasses = ['ic-sub-label']
  if (isLabelDisable) {
    labelClasses.push('disabled')
    subLabelClasses.push('disabled')
  }
  if (isInError) {
    labelClasses.push('error')
  }
  const inputClasses = className ? className.split(' ') : []
  const textClasses = ['input-checkbox-label']
  if (hiddenLabel) {
    textClasses.push('label-hidden')
  }
  inputClasses.push('input-checkbox-input')

  const checkboxAttributes: {
    disabled?: boolean
  } = { disabled }

  return (
    <label className={labelClasses.join(' ')}>
      <input
        checked={checked}
        className={inputClasses.join(' ')}
        name={name}
        onChange={onChange}
        type="checkbox"
        {...checkboxAttributes}
      />
      {SvgElement && <SvgElement aria-hidden />}
      <span className={textClasses.join(' ')}>
        {label}
        {subLabel && (
          <span className={subLabelClasses.join(' ')}>{subLabel}</span>
        )}
      </span>
    </label>
  )
}

export default CheckboxInput
