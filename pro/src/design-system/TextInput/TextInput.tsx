import classNames from 'classnames'
import {
  type ChangeEventHandler,
  type FocusEventHandler,
  type ForwardedRef,
  forwardRef,
  type KeyboardEventHandler,
  useId,
} from 'react'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { FieldFooter } from '../common/FieldFooter/FieldFooter'
import { FieldHeader } from '../common/FieldHeader/FieldHeader'
import styles from './TextInput.module.scss'
import {
  TextInputButton,
  type TextInputButtonProps,
} from './TextInputButton/TextInputButton'

export type TextInputProps = {
  label: string
  type?: React.InputHTMLAttributes<HTMLInputElement>['type']
  name: string
  value?: string
  onChange?: ChangeEventHandler<HTMLInputElement>
  onBlur?: FocusEventHandler<HTMLInputElement>
  onKeyDown?: KeyboardEventHandler<HTMLInputElement>
  disabled?: boolean
  description?: string
  error?: string
  required?: boolean
  asterisk?: boolean
  charactersCount?: {
    current: number
    max: number
  }
  step?: number | string
  min?: number | string
  max?: number | string
  icon?: string
  iconButton?: TextInputButtonProps
  extension?: React.ReactNode
  autoComplete?: React.InputHTMLAttributes<HTMLInputElement>['autoComplete']
  spellCheck?: React.InputHTMLAttributes<HTMLInputElement>['spellCheck']
  describedBy?: string
}

export const TextInput = forwardRef(
  (
    {
      label,
      type = 'text',
      name,
      disabled = false,
      description,
      error,
      required = false,
      asterisk = true,
      charactersCount,
      icon,
      iconButton,
      onChange,
      onBlur,
      onKeyDown,
      value,
      step,
      min,
      extension,
      autoComplete,
      spellCheck,
      describedBy,
    }: TextInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const inputId = useId()
    const descriptionId = useId()
    const errorId = useId()
    const charactersCountId = useId()

    const describedByIds = `${description ? descriptionId : ''} ${error ? errorId : ''} ${charactersCount ? charactersCountId : ''} ${describedBy ?? ''}`

    return (
      <div
        className={classNames(styles['container'], {
          [styles['is-disabled']]: disabled,
          [styles['has-error']]: Boolean(error),
          [styles['has-description']]: Boolean(description),
          [styles['has-icon']]: Boolean(icon),
          [styles['has-button']]: Boolean(iconButton),
        })}
      >
        <div className={styles['header']}>
          <FieldHeader
            description={description}
            descriptionId={descriptionId}
            inputId={inputId}
            label={label}
            required={required}
            asterisk={asterisk}
          />
        </div>
        <div className={styles['input-container']}>
          {icon && (
            <SvgIcon src={icon} alt="" className={styles['input-icon']} />
          )}
          <input
            className={styles['input']}
            id={inputId}
            type={type}
            disabled={disabled}
            aria-describedby={describedByIds}
            aria-invalid={Boolean(error)}
            aria-required={required}
            ref={ref}
            name={name}
            onChange={onChange}
            onBlur={onBlur}
            onKeyDown={onKeyDown}
            value={value}
            maxLength={charactersCount?.max}
            autoComplete={autoComplete}
            spellCheck={type === 'number' ? 'false' : spellCheck}
            step={type === 'number' ? step : undefined}
            min={type === 'number' ? min : undefined}
          />
          {iconButton && (
            <div className={styles['input-button']}>
              <TextInputButton {...iconButton} />
            </div>
          )}
        </div>
        <div className={styles['footer']}>
          <FieldFooter
            charactersCount={charactersCount}
            charactersCountId={charactersCountId}
            error={error}
            errorId={errorId}
          />
        </div>
        {extension && <div className={styles['extension']}>{extension}</div>}
      </div>
    )
  }
)

TextInput.displayName = 'TextInput'
