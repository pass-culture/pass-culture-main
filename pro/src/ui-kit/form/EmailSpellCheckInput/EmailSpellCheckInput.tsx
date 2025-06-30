import { ForwardedRef, forwardRef, useState } from 'react'

import fullNextIcon from 'icons/full-next.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { suggestEmail } from 'ui-kit/form/EmailSpellCheckInput/suggestEmail'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import styles from './EmailSpellCheckInput.module.scss'

type EmailSpellCheckInputProps = {
  name: string
  description: string
  label: string
  onApplyTip(tip: string): void
  overrideInitialTip?: string | null
  maxLength?: number
  required?: boolean
  asterisk?: boolean
  error?: string
  className?: string
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void
}

export const EmailSpellCheckInput = forwardRef(
  (
    {
      name,
      description,
      label,
      className,
      onApplyTip,
      maxLength = 255,
      required,
      asterisk = true,
      error,
      ...props
    }: EmailSpellCheckInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const [emailValidationTip, setEmailValidationTip] = useState<
      string | null
    >()

    const handleEmailValidationOnBlur = (
      event: React.FocusEvent<HTMLInputElement>
    ) => {
      const fieldValue = event.target.value
      if (fieldValue.length > 0) {
        const suggestion = suggestEmail(fieldValue.toString(), !!error)
        if (suggestion) {
          setEmailValidationTip(suggestion)
        } else {
          resetEmailValidation()
        }
      }

      props.onBlur?.(event) // Don't forget to invoke props.onBlur() if it's defined to not break external uses of onBlur()
    }
    const resetEmailValidation = () => {
      setEmailValidationTip(null)
    }

    return (
      <>
        <TextInput
          ref={ref}
          label={label}
          name={name}
          description={description}
          autoComplete="email"
          className={className}
          maxLength={maxLength}
          required={required}
          asterisk={asterisk}
          error={error}
          {...props}
          onBlur={handleEmailValidationOnBlur} // Override props.onBlur() to handle internal behavior that shows the tip
        />
        {emailValidationTip && (
          <div className={styles['email-validation-error']}>
            <div className={styles['email-validation-tip']}>
              Voulez-vous plutôt dire {emailValidationTip} ?
            </div>
            <Button
              variant={ButtonVariant.TERNARY}
              icon={fullNextIcon}
              iconPosition={IconPositionEnum.LEFT}
              onClick={() => {
                onApplyTip(emailValidationTip)
                resetEmailValidation()
              }}
              autoFocus
            >
              Appliquer la modification
            </Button>
          </div>
        )}
      </>
    )
  }
)

EmailSpellCheckInput.displayName = 'EmailSpellCheckInput'
