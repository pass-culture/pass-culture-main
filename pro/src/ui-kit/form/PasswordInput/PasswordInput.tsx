import { useField } from 'formik'
import React, { useState } from 'react'

import { EyeOpenIcon } from 'icons'
import { ReactComponent as StrokeHideIcon } from 'icons/stroke-hide.svg'
import { Button } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import TextInput from '../TextInput'

import styles from './PasswordInput.module.scss'
import ValidationMessageList from './ValidationMessageList'

interface PasswordInputProps {
  label: string
  name: string
  placeholder?: string
  withErrorPreview?: boolean
  autoComplete?: string
}

const PasswordInput = ({
  label,
  name,
  placeholder,
  withErrorPreview = false,
  autoComplete,
  ...props
}: PasswordInputProps): JSX.Element => {
  const [isPasswordHidden, setPasswordHidden] = useState(true)
  const [field] = useField({ name })
  const displayLocalErrors = withErrorPreview && field.value.length > 0

  const handleToggleHidden = (e: React.MouseEvent<HTMLElement>) => {
    e.preventDefault()
    setPasswordHidden(currentSetPasswordHidden => !currentSetPasswordHidden)
  }

  return (
    <div className={styles['password-input-wrapper']}>
      <TextInput
        className={styles['password-input']}
        label={label}
        name={name}
        placeholder={placeholder}
        type={isPasswordHidden ? 'password' : 'text'}
        autoComplete={autoComplete}
        rightButton={() => (
          <Button
            Icon={isPasswordHidden ? StrokeHideIcon : EyeOpenIcon}
            title={
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

export default PasswordInput
