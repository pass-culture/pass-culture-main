import cn from 'classnames'
import React from 'react'

import buttonStyle from 'ui-kit/Button/Button.module.scss'

import style from './BaseFileInput.module.scss'

interface BaseFileInputProps {
  label: string
  fileTypes: string[]
  isValid: boolean
  isDisabled?: boolean
  onChange: React.ChangeEventHandler<HTMLInputElement>
  children?: never
}

export const BaseFileInput = ({
  label,
  isValid,
  fileTypes,
  onChange,
  isDisabled = false,
}: BaseFileInputProps): JSX.Element => (
  <label
    className={cn(
      buttonStyle['button'],
      buttonStyle['button-primary'],
      style['base-file-input-container']
    )}
  >
    {label}
    <input
      accept={fileTypes.join()}
      aria-invalid={!isValid}
      className={style['file-input']}
      onChange={onChange}
      type="file"
      disabled={isDisabled}
    />
  </label>
)
