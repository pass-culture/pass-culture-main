import classNames from 'classnames'
import type React from 'react'
import {
  forwardRef,
  useCallback,
  useEffect,
  useId,
  useImperativeHandle,
  useState,
} from 'react'

import {
  type PassCultureHandledCountryCode,
  PC_HANDLED_PHONE_COUNTRY_CODES,
  PHONE_EXAMPLE_MAP,
} from '@/commons/core/Phone/constants'
import { isCountryCodeHandledByPassCulture } from '@/commons/core/Phone/utils/isCountryCodeHandledByPassCulture'
import { stripPhoneSeparators } from '@/commons/utils/stripPhoneSeparators'
import { FieldFooter } from '@/design-system/common/FieldFooter/FieldFooter'
import type { RequiredIndicator } from '@/design-system/common/types'

import { CountryCodeSelect } from './CodeCountrySelect/CountryCodeSelect'
import styles from './PhoneNumberInput.module.scss'

export type CountryCodeSelectOption = { value: PassCultureHandledCountryCode }
export const countryCodeSelectOptions = PC_HANDLED_PHONE_COUNTRY_CODES.map(
  (countryCode) => ({ value: countryCode })
)

const extractPhoneParts = (
  value: string
): {
  countryCode: PassCultureHandledCountryCode | null
  phoneNumber: string
} => {
  const countryCode = PC_HANDLED_PHONE_COUNTRY_CODES.find((cc) =>
    value.startsWith(cc)
  )
  if (countryCode && isCountryCodeHandledByPassCulture(countryCode)) {
    return {
      countryCode: countryCode,
      phoneNumber: value.substring(countryCode.length),
    }
  }
  return { countryCode: null, phoneNumber: value }
}

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
  /** What type of required indicator is displayed */
  requiredIndicator?: RequiredIndicator
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
      requiredIndicator = 'symbol',
      ...props
    },
    ref
  ) => {
    const countryCodeSelectId = useId()
    const formatId = useId()
    const inputId = useId()
    const errorId = useId()

    const defaultCountryCode = PC_HANDLED_PHONE_COUNTRY_CODES[0]

    // Extract countryCode and nationalNumber to hydrate states from "value"
    const { countryCode: initialCountryCode, phoneNumber: initialPhoneNumber } =
      extractPhoneParts(value)

    // Internal component states (countryCode and nationalNumber)
    const [countryCode, setCountryCode] =
      useState<PassCultureHandledCountryCode>(
        initialCountryCode || defaultCountryCode
      )
    const [phoneNumber, setPhoneNumber] = useState(initialPhoneNumber || '')

    // Function that will updates internal states
    const setCountryCodeAndPhoneNumberFrom = useCallback((value: string) => {
      const { countryCode: newCountryCode, phoneNumber: newPhoneNumber } =
        extractPhoneParts(value)
      setCountryCode(newCountryCode || defaultCountryCode)
      setPhoneNumber(newPhoneNumber)
    }, [])

    // Updates internal states when the "value" prop changes from the outside
    useEffect(() => {
      setCountryCodeAndPhoneNumberFrom(value)
    }, [value, setCountryCodeAndPhoneNumberFrom])

    // When <CountryCodeSelect> changes, combine countryCode and phoneNumber and notify the change up
    // Combine countryCode and phoneNumber, emitting empty string when phoneNumber is empty
    const getCombinedValue = (code: string, number: string) =>
      number ? code + stripPhoneSeparators(number) : ''

    const handleCountryCodeChange = (
      e: React.ChangeEvent<HTMLSelectElement>
    ) => {
      const newCountryCode = e.target.value as PassCultureHandledCountryCode
      setCountryCode(newCountryCode)
      if (onChange) {
        // fire an event object based on the original event, but with the combined value
        onChange({
          ...e,
          target: {
            ...e.target,
            value: getCombinedValue(newCountryCode, phoneNumber),
            name,
          },
        })
      }
    }

    // When input changes, combine countryCode and phoneNumber and notify the change up
    const handleNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const newPhoneNumber = e.target.value
      setPhoneNumber(newPhoneNumber)
      if (onChange) {
        // fire an event object based on the original event, but with the combined value
        onChange({
          ...e,
          target: {
            ...e.target,
            value: getCombinedValue(countryCode, newPhoneNumber),
            name,
          },
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
          target: {
            ...e.target,
            value: getCombinedValue(countryCode, phoneNumber),
            name,
          },
        })
      }
    }

    // This does the trick to combine countryCode and phoneNumber into a single value :
    // It will expose a reference to an dummy input element that can be used by react-hook-form or any other external usage that implies a ref
    useImperativeHandle(ref, () => {
      const element = document.createElement('input')

      Object.defineProperty(element, 'value', {
        get: () => getCombinedValue(countryCode, phoneNumber),
        set: (newValue) => {
          if (!newValue) {
            return
          }

          setCountryCodeAndPhoneNumberFrom(newValue)
        },
      })

      element.name = name || ''

      return element
    })

    return (
      <fieldset className={styles['phone-number-input-wrapper']}>
        <legend className={styles['phone-number-input-legend']}>
          {label}
          {required && requiredIndicator === 'symbol' && <>&nbsp;*</>}
        </legend>
        <div className={styles['phone-number-input-info']}>
          <p className={styles['phone-format']} id={formatId}>
            Par exemple : {PHONE_EXAMPLE_MAP[countryCode]}
          </p>
          {required && requiredIndicator === 'explicit' && (
            <span className={styles['field-header-right']}>Obligatoire</span>
          )}
        </div>
        <div className={styles['phone-number-inpus']}>
          <label
            htmlFor={countryCodeSelectId}
            className={styles['visually-hidden']}
          >
            Indicatif téléphonique
          </label>
          <CountryCodeSelect
            id={countryCodeSelectId}
            disabled={Boolean(disabled)}
            options={countryCodeSelectOptions}
            className={styles['country-code-select']}
            value={countryCode}
            onChange={handleCountryCodeChange}
            onBlur={handleBlur}
          />
          <label htmlFor={inputId} className={styles['visually-hidden']}>
            Numéro de téléphone
          </label>
          <input
            disabled={disabled}
            type="text"
            name={name}
            value={phoneNumber}
            onChange={handleNumberChange}
            onBlur={handleBlur}
            aria-invalid={Boolean(error)}
            id={inputId}
            className={classNames(styles['phone-number-input'], {
              [styles['has-error']]: Boolean(error),
            })}
            autoComplete="tel-national"
            maxLength={maxLength}
            aria-describedby={`${formatId} ${error ? errorId : ''}`}
            {...props}
          />
          <FieldFooter error={error} errorId={errorId} />
        </div>
      </fieldset>
    )
  }
)

PhoneNumberInput.displayName = 'PhoneNumberInput'
