import React, { useState } from 'react'

import { ReactComponent as IcoEyeClose } from 'icons/ico-eye-close.svg'
import { ReactComponent as IcoEyeOpen } from 'icons/ico-eye-open.svg'

import TextInput from '../TextInput'

import styles from './PasswordInput.module.scss'

interface IPasswordInputProps {
  label: string
  name: string
  placeholder: string
}

const PasswordInput = ({
  label,
  name,
  placeholder,
}: IPasswordInputProps): JSX.Element => {
  const [isPasswordHidden, setPasswordHidden] = useState(true)

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
        rightButton={() => (
          <button onClick={handleToggleHidden}>
            {isPasswordHidden ? (
              <IcoEyeClose className={styles['password-input-eye-ico']} />
            ) : (
              <IcoEyeOpen className={styles['password-input-eye-ico']} />
            )}
          </button>
        )}
      />
    </div>
  )
}

export default PasswordInput
