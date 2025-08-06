import cn from 'classnames'
import React, { ForwardedRef, useState } from 'react'

import strokeHideIcon from '@/icons/stroke-hide.svg'
import strokeShowIcon from '@/icons/stroke-show.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { TextInput } from '../TextInput/TextInput'
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
          className={styles['password-input']}
          label={label}
          name={name}
          description={description}
          type={isPasswordHidden ? 'password' : 'text'}
          autoComplete={autoComplete}
          error={error}
          asterisk={asterisk}
          required={required}
          rightButton={() => (
            <Button
              icon={isPasswordHidden ? strokeHideIcon : strokeShowIcon}
              iconAlt={
                isPasswordHidden
                  ? 'Afficher le mot de passe'
                  : 'Cacher le mot de passe'
              }
              onClick={handleToggleHidden}
              variant={ButtonVariant.TERNARY}
            />
          )}
          {...props}
        />
      </div>
    )
  }
)

PasswordInput.displayName = 'PasswordInput'
