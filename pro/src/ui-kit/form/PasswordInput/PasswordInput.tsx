import { useField } from 'formik'
import React, { useState } from 'react'

import { EyeCloseIcon, EyeOpenIcon } from 'icons'

import TextInput from '../TextInput'

import styles from './PasswordInput.module.scss'
import ValidationMessageList from './ValidationMessageList'

interface IPasswordInputProps {
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
}: IPasswordInputProps): JSX.Element => {
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
        hideFooter={displayLocalErrors}
        autoComplete={autoComplete}
        rightButton={() => (
          <button onClick={handleToggleHidden} type="button">
            {isPasswordHidden ? (
              <EyeCloseIcon className={styles['password-input-eye-ico']}>
                Afficher le mot de passe
              </EyeCloseIcon>
            ) : (
              <EyeOpenIcon className={styles['password-input-eye-ico']}>
                Cacher le mot de passe
              </EyeOpenIcon>
            )}
          </button>
        )}
        {...props}
      />
      {displayLocalErrors && <ValidationMessageList name={name} />}
    </div>
  )
}

export default PasswordInput
