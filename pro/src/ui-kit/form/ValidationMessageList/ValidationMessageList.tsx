import cn from 'classnames'
import { useEffect, useState } from 'react'

import {
  getPasswordRuleLabel,
  passwordValidationStatus,
} from '@/ui-kit/form/PasswordInput/validation'
import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'
import { FieldSuccess } from '@/ui-kit/form/shared/FieldSuccess/FieldSuccess'

import styles from './ValidationMessageList.module.scss'

export interface ValidationMessageListProps {
  passwordValue: string
  hasError: boolean
}

export const ValidationMessageList = ({
  passwordValue,
  hasError,
}: ValidationMessageListProps) => {
  const [errors, setErrors] = useState<{ [key: string]: boolean }>({})

  useEffect(() => {
    setErrors(passwordValidationStatus(passwordValue))
  }, [passwordValue])

  return (
    <div className={styles['password-footer']}>
      {Object.keys(errors).map((k) => {
        return (
          <div key={k} className={styles['field-layout-error']}>
            {errors[k] ? (
              <FieldError
                name={getPasswordRuleLabel(k)}
                iconAlt="Il manque "
                className={cn({
                  [styles['field-error-pristine']]: !hasError,
                })}
              >
                {getPasswordRuleLabel(k)}
              </FieldError>
            ) : (
              <FieldSuccess
                name={getPasswordRuleLabel(k)}
                iconAlt="Il y a bien "
              >
                {getPasswordRuleLabel(k)}
              </FieldSuccess>
            )}
          </div>
        )
      })}
    </div>
  )
}
