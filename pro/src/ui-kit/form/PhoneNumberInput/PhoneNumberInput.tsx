import { useField } from 'formik'
import { parsePhoneNumberFromString } from 'libphonenumber-js'
import type { CountryCode } from 'libphonenumber-js'
import { ChangeEvent, FocusEvent, useEffect, useId, useState } from 'react'

import { BaseInput } from '../shared/BaseInput/BaseInput'
import { FieldError } from '../shared/FieldError/FieldError'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import { CountryCodeSelect } from './CodeCountrySelect/CountryCodeSelect'
import { PHONE_CODE_COUNTRY_CODE_OPTIONS, PHONE_EXAMPLE_MAP } from './constants'
import styles from './PhoneNumberInput.module.scss'
import { getPhoneNumberInputAndCountryCode } from './utils/getPhoneNumberInputAndCountryCode'

/**
 * Props for the PhoneNumberInput component.
 *
 * @extends FieldLayoutBaseProps
 */
type PhoneNumberInputProps = FieldLayoutBaseProps & {
  /**
   * Whether the phone number input is disabled.
   */
  disabled?: boolean
  /**
   * Maximum length for the phone number input.
   * @default 25
   */
  maxLength?: number
}

/**
 * The PhoneNumberInput component allows users to input and validate a phone number.
 * It integrates with Formik for form state management and supports country code selection.
 *
 * ---
 * **Important: Avoid using placeholders to indicate phone number format.**
 * Instead, use labels or helper text to ensure accessibility and clarity for all users.
 * ---
 *
 * @param {PhoneNumberInputProps} props - The props for the PhoneNumberInput component.
 * @returns {JSX.Element} The rendered PhoneNumberInput component.
 *
 * @example
 * <PhoneNumberInput
 *   name="phoneNumber"
 *   label="Your Phone Number"
 *   maxLength={15}
 * />
 *
 * @accessibility
 * - **Labels**: Always provide a meaningful label for the phone number input to assist users with screen readers.
 * - **Country Code Selection**: The `CountryCodeSelect` component allows users to choose the correct country code, improving accuracy and reducing input errors.
 * - **Error Handling**: Validation errors are displayed in an accessible manner to ensure that all users are informed of any issues.
 */
export const PhoneNumberInput = ({
  name,
  label,
  disabled,
  isOptional = false,
  maxLength = 25,
}: PhoneNumberInputProps) => {
  const [field, meta, helpers] = useField({ name })

  const formatId = useId()

  const [countryCode, setCountryCode] = useState<CountryCode>(
    PHONE_CODE_COUNTRY_CODE_OPTIONS[0].value
  )
  const [phoneInputValue, setPhoneInputValue] = useState<string>('')

  const validateAndSetPhoneNumber = async (
    phoneNumberInputValue: string,
    currentCountryCode: CountryCode
  ): Promise<string> => {
    const phoneNumber = parsePhoneNumberFromString(
      phoneNumberInputValue,
      currentCountryCode
    )

    // Save formatted phone number i.e +33639980101 even if user types 0639980101 or 639980101
    if (phoneNumber) {
      await helpers.setValue(phoneNumber.number, false)
    }

    setPhoneInputValue(phoneNumberInputValue)

    if (isOptional && phoneNumberInputValue === '') {
      await helpers.setValue('')
      helpers.setError(undefined)
      return phoneNumberInputValue
    }

    if (!phoneNumber || !phoneNumber.isValid()) {
      // If optional, value the formik field with incorrect phone number to raise an error on form validation
      if (isOptional) {
        await helpers.setValue(phoneNumberInputValue)
      }
      helpers.setError(
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678'
      )
      return phoneNumberInputValue
    }

    helpers.setError(undefined)
    return phoneNumber.nationalNumber
  }

  const onPhoneNumberChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const phoneNumberInputValue = event.target.value
    await validateAndSetPhoneNumber(phoneNumberInputValue, countryCode)
  }

  const onPhoneCodeChange = async (e: ChangeEvent<HTMLSelectElement>) => {
    const changedCountryCode = e.target.value as CountryCode
    setCountryCode(changedCountryCode)
    if (phoneInputValue) {
      await validateAndSetPhoneNumber(phoneInputValue, changedCountryCode)
    }
  }

  const onPhoneNumberBlur = async (event: FocusEvent<HTMLInputElement>) => {
    if (!meta.touched) {
      await helpers.setTouched(true, false)
    }

    const phoneNumberInputValue = await validateAndSetPhoneNumber(
      event.target.value,
      countryCode
    )
    setPhoneInputValue(phoneNumberInputValue)
  }

  useEffect(() => {
    try {
      const { inputValue, countryCode: computedCountryCode } =
        getPhoneNumberInputAndCountryCode(field.value)
      setCountryCode(computedCountryCode)
      setPhoneInputValue(inputValue)
    } catch (e) {
      helpers.setError(e as string)
    }
  }, [field.value])

  return (
    <fieldset className={styles['phone-number-input-wrapper']}>
      <legend className={styles['phone-number-input-legend']}>
        {label} {!isOptional && '*'}
      </legend>
      <p className={styles['phone-format']} id={formatId}>
        Par exemple : {PHONE_EXAMPLE_MAP[countryCode]}
      </p>
      <div className={styles['phone-number-inpus']}>
        <label htmlFor="countryCode" className={styles['visually-hidden']}>
          Indicatif téléphonique
        </label>
        <CountryCodeSelect
          disabled={Boolean(disabled)}
          options={PHONE_CODE_COUNTRY_CODE_OPTIONS}
          className={styles['country-code-select']}
          value={countryCode}
          onChange={onPhoneCodeChange}
        />

        <label htmlFor={name} className={styles['visually-hidden']}>
          Numéro de téléphone
        </label>
        <BaseInput
          disabled={disabled}
          hasError={meta.touched && !!meta.error}
          type="text"
          name={name}
          value={phoneInputValue}
          onChange={onPhoneNumberChange}
          className={styles['phone-number-input']}
          onBlur={onPhoneNumberBlur}
          autoComplete="tel-national"
          maxLength={maxLength}
          aria-describedby={formatId}
        />
        <div className={styles['phone-number-input-footer']}>
          {meta.error && meta.touched && (
            <div className={styles['phone-number-input-error']}>
              <FieldError name={name}>{meta.error}</FieldError>
            </div>
          )}
        </div>
      </div>
    </fieldset>
  )
}
