import React, {
  forwardRef,
  useCallback,
  useEffect,
  useId,
  useImperativeHandle,
  useState,
} from 'react'

import { BaseInput } from '@/ui-kit/form/shared/BaseInput/BaseInput'
import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'

import { CountryCodeSelect } from './CodeCountrySelect/CountryCodeSelect'
import {
  PHONE_CODE_COUNTRY_CODE_OPTIONS,
  PHONE_EXAMPLE_MAP,
  PlusString,
} from './constants'
import styles from './PhoneNumberInput.module.scss'

export type PhoneNumberInputProps = {
  // native props that are used by react-hook-form’s register() function
  value?: string
  onChange?: (e: { target: { value: string; name?: string } }) => void
  onBlur?: (e: React.FocusEvent<HTMLSelectElement | HTMLInputElement>) => void
  name: string
  ref?: React.Ref<HTMLInputElement>
  // other business-oriented props
  disabled?: boolean
  maxLength?: number
  error?: string
  label: string | JSX.Element
  required?: boolean
  asterisk?: boolean
}

export const PhoneNumberInput = forwardRef<
  HTMLInputElement,
  PhoneNumberInputProps
>(
  (
    {
      value = '',
      onChange,
      onBlur,
      name,
      disabled,
      maxLength = 25,
      error,
      label,
      required = false,
      asterisk = true,
      ...props
    },
    ref
  ) => {
    const formatId = useId()

    const defaultPrefix = PHONE_CODE_COUNTRY_CODE_OPTIONS[0].value

    // Initialize states with given value (splits prefix "+33" and phone number "612345678")
    const { prefix: initialPrefix, phoneNumber: initialPhoneNumber } =
      extractPhoneParts(value)

    const [prefix, setPrefix] = useState(initialPrefix || defaultPrefix)
    const [phoneNumber, setPhoneNumber] = useState(initialPhoneNumber)

    // Function that will updates internal states
    const setPrefixAndPhoneNumberFrom = useCallback(
      (value: string) => {
        const { prefix: newPrefix, phoneNumber: newPhoneNumber } =
          extractPhoneParts(value)
        setPrefix(newPrefix || defaultPrefix)
        setPhoneNumber(newPhoneNumber)
      },
      [defaultPrefix]
    )

    // Updates internal states when the "value" prop changes from the outside
    useEffect(() => {
      setPrefixAndPhoneNumberFrom(value)
    }, [value, setPrefixAndPhoneNumberFrom])

    // When <CountryCodeSelect> changes, combine prefix and phone number and notify the change up
    const handlePrefixChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      const newPrefix = e.target.value
      setPrefix(newPrefix)
      if (onChange) {
        // fire an event object based on the original event, but with the combined value
        onChange({
          ...e,
          target: { ...e.target, value: newPrefix + phoneNumber, name },
        })
      }
    }

    // When <BaseInput> changes, combine prefix and phone number and notify the change up
    const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newPhoneNumber = e.target.value
      setPhoneNumber(newPhoneNumber)
      if (onChange) {
        // fire an event object based on the original event, but with the combined value
        onChange({
          ...e,
          target: { ...e.target, value: prefix + newPhoneNumber, name },
        })
      }
    }

    // Handles onBlur events
    const handleBlur = (
      e: React.FocusEvent<HTMLSelectElement | HTMLInputElement>
    ) => {
      if (onBlur) {
        // fire an event object based on the original event, but with the combined value
        onBlur({
          ...e,
          target: { ...e.target, value: prefix + phoneNumber, name },
        })
      }
    }

    // This does the trick to combine prefix and phone number into a single value :
    // It will expose a reference to an dummy input element that can be used by react-hook-form or any other external usage that implies a ref
    useImperativeHandle(ref, () => {
      const element = document.createElement('input')

      Object.defineProperty(element, 'value', {
        get: () => prefix + phoneNumber,
        set: (newValue) => {
          setPrefixAndPhoneNumberFrom(newValue)
        },
      })

      element.name = name || ''

      return element
    })

    return (
      <fieldset className={styles['phone-number-input-wrapper']}>
        <legend className={styles['phone-number-input-legend']}>
          {label} {required && asterisk && '*'}
        </legend>
        <p className={styles['phone-format']} id={formatId}>
          Par exemple : {PHONE_EXAMPLE_MAP[prefix as PlusString]}
        </p>
        <div className={styles['phone-number-inpus']}>
          <label htmlFor="countryCode" className={styles['visually-hidden']}>
            Indicatif téléphonique
          </label>
          <CountryCodeSelect
            disabled={Boolean(disabled)}
            options={PHONE_CODE_COUNTRY_CODE_OPTIONS}
            className={styles['country-code-select']}
            value={prefix}
            onChange={handlePrefixChange}
            onBlur={handleBlur}
          />

          <label htmlFor={name} className={styles['visually-hidden']}>
            Numéro de téléphone
          </label>
          <BaseInput
            disabled={disabled}
            hasError={!!error}
            type="text"
            name={name}
            value={phoneNumber}
            onChange={handleNumberChange}
            onBlur={handleBlur}
            className={styles['phone-number-input']}
            autoComplete="tel-national"
            maxLength={maxLength}
            aria-describedby={formatId}
            {...props}
          />
          <div className={styles['phone-number-input-footer']}>
            {error && (
              <div className={styles['phone-number-input-error']}>
                <FieldError name={name}>{error}</FieldError>
              </div>
            )}
          </div>
        </div>
      </fieldset>
    )
  }
)

PhoneNumberInput.displayName = 'PhoneNumberInput'

/**
 * Splits a phone number into a valid prefix and phone number.
 *
 * @param {string} fullNumber - The full phone number including the country code prefix.
 * @returns {{ prefix: string, phoneNumber: string }} An object containing the extracted prefix and phone number.
 *
 * @example
 * // returns { prefix: "+33", phoneNumber: "612345678" }
 * extractPhoneParts("+33612345678")
 */
export const extractPhoneParts = (fullNumber: string) => {
  const prefixes = PHONE_CODE_COUNTRY_CODE_OPTIONS.map((o) => o.value)
  const foundPrefix = prefixes.find((p) => fullNumber.startsWith(p))

  if (foundPrefix) {
    return {
      prefix: foundPrefix,
      phoneNumber: fullNumber.substring(foundPrefix.length),
    }
  }

  return { prefix: '', phoneNumber: fullNumber }
}
