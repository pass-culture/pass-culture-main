import cn from 'classnames'
import React from 'react'

import style from './BaseFileInput.module.scss'

export interface IBaseFileInputProps {
  label: string
  fileTypes: string[]
  isValid: boolean
  onChange: React.ChangeEventHandler<HTMLInputElement>
  children?: never
}

const BaseFileInput = ({
  label,
  isValid,
  fileTypes,
  onChange,
}: IBaseFileInputProps): JSX.Element => (
  <label className={cn('primary-link ', style['base-file-input-container'])}>
    {label}
    <input
      accept={fileTypes.join()}
      aria-invalid={isValid}
      className={style['file-input']}
      onChange={onChange}
      type="file"
    />
  </label>
)

export default BaseFileInput
