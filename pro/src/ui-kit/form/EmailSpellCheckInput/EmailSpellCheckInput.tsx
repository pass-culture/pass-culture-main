import { useField, useFormikContext } from 'formik'
import React, { useState } from 'react'

import { CircleArrowIcon } from 'icons'
import { Button } from 'ui-kit/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { suggestEmail } from 'ui-kit/form/EmailSpellCheckInput/suggestEmail'
import { TextInput } from 'ui-kit/form/index'

import styles from './EmailSpellCheckInput.module.scss'

export interface IEmailSpellCheckInputProps<FormType> {
  // `Extract` needed so the key is a string. See https://stackoverflow.com/a/51808262
  name: Extract<keyof FormType, string>
  placeholder: string
  label: string
  overrideInitialTip?: string | null
}

const EmailSpellCheckInput = <FormType,>({
  name,
  placeholder,
  label,
  overrideInitialTip = null,
}: IEmailSpellCheckInputProps<FormType>): JSX.Element => {
  const { setFieldValue, setFieldTouched } = useFormikContext<FormType>()
  const [field, meta] = useField<string>(name)
  const [emailValidationTip, setEmailValidationTip] = useState<string | null>(
    overrideInitialTip
  )

  const handleEmailValidation = () => {
    if (field.value.length > 0) {
      const suggestion = suggestEmail(
        field.value.toString(),
        Boolean(meta.error)
      )
      if (suggestion) {
        setEmailValidationTip(suggestion)
      }
      setFieldTouched(field.name, true)
    }
  }
  const resetEmailValidation = () => {
    setEmailValidationTip(null)
  }

  const applyTip = () => {
    setFieldValue(name, emailValidationTip, true)
    setEmailValidationTip(null)
  }

  return (
    <>
      <TextInput
        label={label}
        name={name}
        placeholder={placeholder}
        onBlur={handleEmailValidation}
        onFocus={resetEmailValidation}
        hideFooter={emailValidationTip != null} // This is needed to hide the footer div that takes some space
        autoComplete="email"
      />
      {emailValidationTip && (
        <div className={styles['email-validation-error']}>
          <div className={styles['email-validation-tip']}>
            Voulez-vous plutôt dire {emailValidationTip} ?
          </div>
          <Button
            variant={ButtonVariant.TERNARY}
            Icon={CircleArrowIcon}
            iconPosition={IconPositionEnum.LEFT}
            onClick={applyTip}
            autoFocus
          >
            Appliquer la modification
          </Button>
        </div>
      )}
    </>
  )
}

export default EmailSpellCheckInput
