import cn from 'classnames'
import React, {
  type ChangeEventHandler,
  type ForwardedRef,
  useId,
  useState,
} from 'react'

import {
  TextInput,
  type TextInputProps,
} from '@/design-system/TextInput/TextInput'
import strokeHideIcon from '@/icons/full-hide.svg'
import strokeShowIcon from '@/icons/full-show.svg'

import styles from './PasswordInput.module.scss'
import { ValidationMessageList } from './ValidationMessageList/ValidationMessageList'
import { isPasswordValid } from './validation'

export interface PasswordInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  name: string
  description?: string
  autoComplete?: string
  value: string
  onChange: ChangeEventHandler<HTMLInputElement>
  error?: string
  requiredIndicator?: TextInputProps['requiredIndicator']
  required?: boolean
  disabled?: boolean
  displayValidation?: boolean
}

export const PasswordInput = React.forwardRef(
  (
    {
      value,
      label,
      name,
      description,
      autoComplete,
      error: externalError,
      requiredIndicator,
      required,
      disabled,
      displayValidation,
      onBlur,
      ...props
    }: PasswordInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const passwordFieldId = useId()
    const [isPasswordHidden, setIsPasswordHidden] = useState(true)
    const [wasBlurred, setWasBlurred] = useState(false)
    const showError =
      !!externalError ||
      (wasBlurred && displayValidation && !isPasswordValid(value))

    const handleToggleHidden = (e: React.MouseEvent<HTMLElement>) => {
      e.preventDefault()
      setIsPasswordHidden(
        (currentSetPasswordHidden) => !currentSetPasswordHidden
      )
    }

    const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
      setWasBlurred(true)
      if (onBlur) {
        onBlur(e)
      }
    }

    const passwordIcon = isPasswordHidden ? strokeHideIcon : strokeShowIcon

    return (
      <>
        <div
          className={cn([styles['password-input-wrapper']], {
            [styles['password-input-wrapper-error']]: showError,
          })}
        >
          <TextInput
            ref={ref}
            label={label}
            name={name}
            description={description}
            type={isPasswordHidden || disabled ? 'password' : 'text'}
            autoComplete={autoComplete}
            error={
              showError
                ? externalError || 'Veuillez respecter les conditions requises'
                : undefined
            }
            requiredIndicator={requiredIndicator}
            required={required}
            iconButton={{
              icon: disabled ? '' : passwordIcon,
              label: isPasswordHidden
                ? 'Afficher le mot de passe'
                : 'Cacher le mot de passe',
              onClick: handleToggleHidden,
            }}
            disabled={disabled}
            describedBy={passwordFieldId}
            onBlur={handleBlur}
            {...props}
          />
        </div>
        {displayValidation && (
          <ValidationMessageList
            passwordValue={value}
            fieldName={passwordFieldId}
          />
        )}
      </>
    )
  }
)

PasswordInput.displayName = 'PasswordInput'
