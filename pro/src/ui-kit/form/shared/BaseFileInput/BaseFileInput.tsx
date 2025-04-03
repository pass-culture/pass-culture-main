import cn from 'classnames'

import buttonStyle from 'ui-kit/Button/Button.module.scss'

import style from './BaseFileInput.module.scss'

interface BaseFileInputProps {
  label: string
  fileTypes: string[]
  isValid: boolean
  isDisabled?: boolean
  onChange: React.ChangeEventHandler<HTMLInputElement>
  children?: React.ReactNode | React.ReactNode[]
  ariaDescribedBy?: string
}

export const BaseFileInput = ({
  label,
  isValid,
  fileTypes,
  onChange,
  isDisabled = false,
  ariaDescribedBy,
  children,
}: BaseFileInputProps): JSX.Element => (
  <label
    className={cn({
      [cn(
        buttonStyle['button'],
        buttonStyle['button-primary'],
        style['base-file-input-container']
      )]: Boolean(!children),
    })}
  >
    {children ? children : label}
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
