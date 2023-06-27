import { useField } from 'formik'
import React, { useState } from 'react'

import TextInput from '../TextInput'

import styles from './PasswordInput.module.scss'
import ValidationMessageList from './ValidationMessageList'

interface IPasswordInputProps {
  label: string
  name: string
  placeholder?: string
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
        rightButton={() => (
          <button onClick={handleToggleHidden} type="button">
            h{' '}
          </button>
        )}
      />
      {displayLocalErrors && <ValidationMessageList name={name} />}
    </div>
  )
}

export default PasswordInput
