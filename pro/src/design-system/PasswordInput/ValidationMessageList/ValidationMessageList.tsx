import { useEffect, useState } from 'react'
import { useDebounce } from 'use-debounce'

import { MessageDispatcher } from '@/design-system/PasswordInput/ValidationMessageList/MessageDispatcher/MessageDispatcher'
import {
  getPasswordRuleLabel,
  passwordValidationStatus,
} from '@/design-system/PasswordInput/validation'

import styles from './ValidationMessageList.module.scss'

export interface ValidationMessageListProps {
  passwordValue: string
  fieldName: string
}

export const ValidationMessageList = ({
  passwordValue,
  fieldName,
}: ValidationMessageListProps) => {
  const [errors, setErrors] = useState<{ [key: string]: boolean }>({})
  const [debouncedPassword] = useDebounce(passwordValue, 3000)

  useEffect(() => {
    setErrors(passwordValidationStatus(passwordValue))
  }, [passwordValue])

  const isPristine = !debouncedPassword

  return (
    <div id={fieldName}>
      {isPristine && (
        <div className={styles['sr-only']}>
          Le mot de passe doit comporter :
        </div>
      )}
      <ul
        className={styles['validation-message-list']}
        aria-live="polite"
        aria-atomic="true"
      >
        {Object.keys(errors).map((k) => (
          <li key={k}>
            <MessageDispatcher
              isPristine={isPristine}
              isOnError={errors[k]}
              message={getPasswordRuleLabel(k)}
            />
          </li>
        ))}
      </ul>
    </div>
  )
}
