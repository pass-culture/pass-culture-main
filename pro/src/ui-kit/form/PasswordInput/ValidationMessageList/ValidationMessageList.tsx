import { useField } from 'formik'
import { useEffect, useState } from 'react'

import {
  getPasswordRuleLabel,
  passwordValidationStatus,
} from 'commons/core/shared/utils/validation'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'
import { FieldSuccess } from 'ui-kit/form/shared/FieldSuccess/FieldSuccess'

import styles from './ValidationMessageList.module.scss'

interface ValidationMessageListProps {
  name: string
}

export const ValidationMessageList = ({ name }: ValidationMessageListProps) => {
  const [field] = useField({ name })
  const [errors, setErrors] = useState<{ [key: string]: boolean }>({})

  useEffect(() => {
    setErrors(passwordValidationStatus(field.value))
  }, [field.value])

  return (
    <div className={styles['password-footer']}>
      {Object.keys(errors).map((k) => {
        return (
          <div key={k} className={styles['field-layout-error']}>
            {errors[k] ? (
              <FieldError name={getPasswordRuleLabel(k)} iconAlt="Il manque ">
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
