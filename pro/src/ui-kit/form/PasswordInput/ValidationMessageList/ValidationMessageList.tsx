import { useField } from 'formik'
import React, { useEffect, useState } from 'react'

import {
  getPasswordRuleLabel,
  passwordValidationStatus,
} from 'core/shared/utils/validation'

import { FieldError, FieldSuccess } from '../../shared'

import styles from './ValidationMessageList.module.scss'

interface ValidationMessageListProps {
  name: string
}

const ValidationMessageList = ({ name }: ValidationMessageListProps) => {
  const [field, , helpers] = useField({ name })
  const [errors, setErrors] = useState<{ [key: string]: boolean }>({})

  useEffect(() => {
    setErrors(passwordValidationStatus(field.value))
    // hide base error message and display only localErrors
    helpers.setError('')
  }, [field.value])

  return (
    <div className={styles['password-footer']}>
      {Object.keys(errors).map(k => {
        return (
          <div key={k} className={styles['field-layout-error']}>
            {errors[k] ? (
              <FieldError name={getPasswordRuleLabel(k)}>
                {getPasswordRuleLabel(k)}
              </FieldError>
            ) : (
              <FieldSuccess name={getPasswordRuleLabel(k)}>
                {getPasswordRuleLabel(k)}
              </FieldSuccess>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default ValidationMessageList
