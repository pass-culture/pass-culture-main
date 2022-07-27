import React, { useState } from 'react'

import Icon from 'components/layout/Icon'
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

  const renderPasswordTooltip = () => {
    return `Votre mot de passe doit contenir au moins :
        <ul>
          <li>12 caractères</li>
          <li>une majuscule et une minuscule</li>
          <li>un chiffre</li>
          <li>un caractère spécial (signe de ponctuation, symbole monétaire ou mathématique)</li>
        </ul>`
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
            {isPasswordHidden ? <IcoEyeClose /> : <IcoEyeOpen />}
          </button>
        )}
      />

      <Icon
        alt="Caractéristiques obligatoires du mot de passe"
        className={styles['password-tip-icon']}
        data-place="bottom"
        data-tip={renderPasswordTooltip()}
        data-type="info"
        svg="picto-info"
      />
    </div>
  )
}

export default PasswordInput
