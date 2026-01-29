import cn from 'classnames'

import style from './BaseFileInput.module.scss'

interface BaseFileInputProps {
  label: string
  fileTypes: string[]
  isValid: boolean
  isDisabled?: boolean
  onChange: React.ChangeEventHandler<HTMLInputElement>
  children?: never
  ariaDescribedBy?: string
}

export const BaseFileInput = ({
  label,
  isValid,
  fileTypes,
  onChange,
  isDisabled = false,
  ariaDescribedBy,
}: BaseFileInputProps): JSX.Element => (
  <label
    className={cn(
      style['button'],
      style['button-primary'],
      style['base-file-input-container']
    )}
  >
    {label}
    <input
      accept={fileTypes.join()}
      aria-invalid={!isValid}
      {...(ariaDescribedBy ? { 'aria-describedby': ariaDescribedBy } : {})}
      className={style['file-input']}
      onChange={onChange}
      type="file"
      disabled={isDisabled}
    />
  </label>
)
