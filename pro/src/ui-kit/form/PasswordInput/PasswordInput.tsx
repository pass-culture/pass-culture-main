import cn from 'classnames'
import React, { type ForwardedRef, useState } from 'react'

import { TextInput } from '@/design-system/TextInput/TextInput'
import strokeHideIcon from '@/icons/full-hide.svg'
import strokeShowIcon from '@/icons/full-show.svg'

import styles from './PasswordInput.module.scss'

export interface PasswordInputProps {
  label: string
  name: string
  description?: string
  autoComplete?: string
  error?: string
  asterisk?: boolean
  required?: boolean
}

export const PasswordInput = React.forwardRef(
  (
    {
      label,
      name,
      description,
      autoComplete,
      error,
      asterisk = true,
      required,
      ...props
    }: PasswordInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const [isPasswordHidden, setPasswordHidden] = useState(true)
    const showError = !!error

    const handleToggleHidden = (e: React.MouseEvent<HTMLElement>) => {
      e.preventDefault()
      setPasswordHidden((currentSetPasswordHidden) => !currentSetPasswordHidden)
    }

    return (
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
          type={isPasswordHidden ? 'password' : 'text'}
          autoComplete={autoComplete}
          error={error}
          asterisk={asterisk}
          required={required}
          iconButton={{
            icon: isPasswordHidden ? strokeHideIcon : strokeShowIcon,
            label: isPasswordHidden
              ? 'Afficher le mot de passe'
              : 'Cacher le mot de passe',
            onClick: handleToggleHidden,
          }}
          {...props}
        />
      </div>
    )
  }
)

PasswordInput.displayName = 'PasswordInput'
