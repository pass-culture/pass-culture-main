import { type ForwardedRef, forwardRef, type JSX, useState } from 'react'

import { TextInput } from '@/design-system/TextInput/TextInput'
import fullNextIcon from '@/icons/full-next.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant, IconPositionEnum } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { suggestEmail } from '@/ui-kit/form/EmailSpellCheckInput/suggestEmail'

import styles from './EmailSpellCheckInput.module.scss'

type EmailSpellCheckInputProps = {
  name: string
  description: string
  label: string
  onApplyTip(tip: string): void
  required?: boolean
  error?: string
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void
  currentCount: number
}

export const EmailSpellCheckInput = forwardRef(
  (
    {
      name,
      description,
      label,
      onApplyTip,
      required,
      error,
      currentCount,
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
          maxCharactersCount={255}
          required={required}
          error={error}
          {...props}
          onBlur={handleEmailValidationOnBlur} // Override props.onBlur() to handle internal behavior that shows the tip
        />
        {emailValidationTip && (
          <Callout className={styles['email-validation-error']}>
            <p>Voulez-vous plutôt dire {emailValidationTip} ?</p>
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
          </Callout>
        )}
      </>
    )
  }
)

EmailSpellCheckInput.displayName = 'EmailSpellCheckInput'
