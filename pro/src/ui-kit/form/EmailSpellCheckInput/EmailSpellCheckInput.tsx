import { useField, useFormikContext } from 'formik'
import React, { useState } from 'react'

import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { suggestEmail } from 'ui-kit/form/EmailSpellCheckInput/suggestEmail'
import { FieldLayoutBaseProps } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import { TextInput } from '../TextInput/TextInput'

import styles from './EmailSpellCheckInput.module.scss'

type EmailSpellCheckInputProps<FormType> = FieldLayoutBaseProps & {
  // `Extract` needed so the key is a string. See https://stackoverflow.com/a/51808262
  name: Extract<keyof FormType, string>
  placeholder?: string
  description: string
  label: string
  overrideInitialTip?: string | null
  maxLength?: number
}

export const EmailSpellCheckInput = <FormType,>({
  name,
  placeholder,
  description,
  label,
  className,
  overrideInitialTip = null,
  maxLength = 255,
}: EmailSpellCheckInputProps<FormType>): JSX.Element => {
  const { setFieldValue, setFieldTouched } = useFormikContext<FormType>()
  const [field, meta] = useField<string>(name)
  const [emailValidationTip, setEmailValidationTip] = useState<string | null>(
    overrideInitialTip
  )

  const handleEmailValidation = async () => {
    if (field.value.length > 0) {
      const suggestion = suggestEmail(
        field.value.toString(),
        Boolean(meta.error)
      )
      if (suggestion) {
        setEmailValidationTip(suggestion)
      }
    }
    await setFieldTouched(field.name, true)
  }
  const resetEmailValidation = () => {
    setEmailValidationTip(null)
  }

  const applyTip = async () => {
    await setFieldValue(name, emailValidationTip, true)
    setEmailValidationTip(null)
  }

  return (
    <>
      <TextInput
        label={label}
        name={name}
        placeholder={placeholder}
        description={description}
        onBlur={handleEmailValidation}
        onFocus={resetEmailValidation}
        hideFooter={emailValidationTip !== null} // This is needed to hide the footer div that takes some space
        autoComplete="email"
        className={className}
        maxLength={maxLength}
        ErrorDetails={
          emailValidationTip ? (
            <div className={styles['email-validation-error']}>
              <div className={styles['email-validation-tip']}>
                Voulez-vous plutôt dire {emailValidationTip} ?
              </div>
              <Button
                variant={ButtonVariant.TERNARY}
                icon={fullNextIcon}
                iconPosition={IconPositionEnum.LEFT}
                onClick={applyTip}
                autoFocus
              >
                Appliquer la modification
              </Button>
            </div>
          ) : (
            <></>
          )
        }
      />
    </>
  )
}
