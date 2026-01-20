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
  const [debouncedPassword] = useDebounce(passwordValue, 2000)

  useEffect(() => {
    setErrors(passwordValidationStatus(passwordValue))
  }, [passwordValue])

  const isPristine = !debouncedPassword

  // used for a11y, voice over doesn't manage to read validation otherwise
  const announcementText = Object.keys(errors)
    .map((k) => {
      const label = getPasswordRuleLabel(k)
      const status = errors[k] ? 'Il manque : ' : 'Il y a bien : '
      return `${status} ${label}`
    })
    .join('. ')

  const criteria = Object.keys(errors)
    .map((k) => {
      const label = getPasswordRuleLabel(k)
      return `${label}`
    })
    .join(' ')

  return (
    <div id={fieldName}>
      {isPristine && (
        <div className={styles['sr-only']}>
          Le mot de passe doit comporter : {criteria}
        </div>
      )}
      <div className={styles['sr-only']} aria-live="polite" aria-atomic="true">
        {!isPristine && `Mises à jour des critères : ${announcementText}`}
      </div>
      <ul className={styles['validation-message-list']} aria-hidden={true}>
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
