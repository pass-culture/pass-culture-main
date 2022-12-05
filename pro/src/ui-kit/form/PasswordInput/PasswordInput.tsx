import { useField } from 'formik'
import React, { useEffect, useState } from 'react'

import { ReactComponent as IcoEyeClose } from 'icons/ico-eye-close.svg'
import { ReactComponent as IcoEyeOpen } from 'icons/ico-eye-open.svg'

import TextInput from '../TextInput'

import styles from './PasswordInput.module.scss'
import ValidationMessageList from './ValidationMessageList'

interface IPasswordInputProps {
  label: string
  name: string
  placeholder: string
  withErrorPreview?: boolean
}

const PasswordInput = ({
  label,
  name,
  placeholder,
  withErrorPreview = false,
}: IPasswordInputProps): JSX.Element => {
  const [isPasswordHidden, setPasswordHidden] = useState(true)
  const [field] = useField({ name })
  const [displayLocalErrors, setDisplayLocalErrors] = useState(false)

  useEffect(() => {
    if (withErrorPreview) {
      // We only handle locally the password requirements.
      // The other errors are handled by the FieldLayout.
      setDisplayLocalErrors(field.value.length > 0)
    }
  }, [withErrorPreview, field.value])

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
        rightButton={() => (
          <button onClick={handleToggleHidden}>
            {isPasswordHidden ? (
              <IcoEyeClose className={styles['password-input-eye-ico']}>
                Afficher le mot de passe
              </IcoEyeClose>
            ) : (
              <IcoEyeOpen className={styles['password-input-eye-ico']}>
                Cacher le mot de passe
              </IcoEyeOpen>
            )}
          </button>
        )}
      />
      {displayLocalErrors && <ValidationMessageList name={name} />}
    </div>
  )
}

export default PasswordInput
