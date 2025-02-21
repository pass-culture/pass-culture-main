import cn from 'classnames'
import { useField } from 'formik'
import React, { useState } from 'react'

import strokeHideIcon from 'icons/stroke-hide.svg'
import strokeShowIcon from 'icons/stroke-show.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { TextInput } from '../TextInput/TextInput'

import styles from './PasswordInput.module.scss'
import { ValidationMessageList } from './ValidationMessageList/ValidationMessageList'

interface PasswordInputProps {
  label: string
  name: string
  description?: string
  withErrorPreview?: boolean
  autoComplete?: string
  hideAsterisk?: boolean
}

export const PasswordInput = ({
  label,
  name,
  description,
  withErrorPreview = false,
  autoComplete,
  hideAsterisk = false,
  ...props
}: PasswordInputProps): JSX.Element => {
  const [isPasswordHidden, setPasswordHidden] = useState(true)
  const [field, meta] = useField({ name })
  const displayLocalErrors = withErrorPreview && field.value.length > 0
  const errorShown = (meta.touched && !!meta.error) || displayLocalErrors

  const handleToggleHidden = (e: React.MouseEvent<HTMLElement>) => {
    e.preventDefault()
    setPasswordHidden((currentSetPasswordHidden) => !currentSetPasswordHidden)
  }

  return (
    <div
      className={cn([styles['password-input-wrapper']], {
        [styles['password-input-wrapper-error']]: errorShown,
      })}
    >
      <TextInput
        className={styles['password-input']}
        label={label}
        name={name}
        description={description}
        type={isPasswordHidden ? 'password' : 'text'}
        autoComplete={autoComplete}
        hideAsterisk={hideAsterisk}
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
        ErrorDetails={
          displayLocalErrors && <ValidationMessageList name={name} />
        }
        {...props}
      />
    </div>
  )
}
