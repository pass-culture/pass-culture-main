import { useField } from 'formik'
import { parsePhoneNumberFromString } from 'libphonenumber-js'
import type { CountryCode } from 'libphonenumber-js'
import React, { ChangeEvent, FocusEvent, useEffect, useState } from 'react'

import { BaseInput, FieldError } from '../shared'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import CodeCountrySelect from './CodeCountrySelect/CountryCodeSelect'
import { PHONE_CODE_COUNTRY_CODE_OPTIONS, PLACEHOLDER_MAP } from './constants'
import styles from './PhoneNumberInput.module.scss'
import { getPhoneNumberInputAndCountryCode } from './utils/getPhoneNumberInputAndCountryCode'

export type PhoneNumberInputProps = FieldLayoutBaseProps & {
  disabled?: boolean
}

const PhoneNumberInput = ({
  name,
  label,
  disabled,
  isOptional = false,
}: PhoneNumberInputProps) => {
  const [field, meta, helpers] = useField({ name })

  const [countryCode, setCountryCode] = useState<CountryCode>(
    PHONE_CODE_COUNTRY_CODE_OPTIONS[0].value
  )
  const [phoneInputValue, setPhoneInputValue] = useState<string>('')

  const validatePhoneNumber = (
    phoneNumberInputValue: string
  ): string | undefined => {
    const phoneNumber = parsePhoneNumberFromString(
      phoneNumberInputValue,
      countryCode
    )

    // save formatted phone number i.e +33639980101 even if user types 0639980101 or 639980101
    if (phoneNumber) {
      helpers.setValue(phoneNumber?.number, false)
    }

    setPhoneInputValue(phoneNumberInputValue)

    if (isOptional && phoneNumberInputValue === '') {
      helpers.setValue('')
      helpers.setError(undefined)
      return phoneNumberInputValue
    }

    if (!phoneNumber || !phoneNumber.isValid()) {
      // input optional -> if optional we want to value formik field with incorrect phone number to raise error on form validation
      isOptional && helpers.setValue(phoneNumberInputValue)
      helpers.setError('Veuillez entrer un numéro de téléphone valide')
      return phoneNumberInputValue
    }

    helpers.setError(undefined)
    return phoneNumber?.nationalNumber
  }

  const onPhoneNumberChange = (event: ChangeEvent<HTMLInputElement>) => {
    const phoneNumberInputValue = event.target.value
    validatePhoneNumber(phoneNumberInputValue)
  }

  const onPhoneCodeChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setCountryCode(e.target.value as CountryCode)
    if (phoneInputValue) {
      validatePhoneNumber(phoneInputValue)
    }
  }

  const onPhoneNumberBlur = (event: FocusEvent<HTMLInputElement>) => {
    if (!meta.touched) {
      helpers.setTouched(true, false)
    }

    const phoneNumberInputValue = validatePhoneNumber(event.target.value) ?? ''
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
        {label}
        {isOptional && (
          <span className={styles['phone-number-input-optional']}>
            Optionnel
          </span>
        )}
      </legend>
      <label htmlFor="countryCode" className={styles['label-hidden']}>
        Indicatif téléphonique
      </label>
      <CodeCountrySelect
        disabled={Boolean(disabled)}
        options={PHONE_CODE_COUNTRY_CODE_OPTIONS}
        className={styles['country-code-select']}
        value={countryCode}
        onChange={onPhoneCodeChange}
      />

      <label htmlFor={name} className={styles['label-hidden']}>
        Numéro de téléphone
      </label>
      <BaseInput
        disabled={disabled}
        hasError={meta.touched && !!meta.error}
        placeholder={PLACEHOLDER_MAP[countryCode]}
        type="text"
        name={name}
        value={phoneInputValue}
        onChange={onPhoneNumberChange}
        className={styles['phone-number-input']}
        onBlur={onPhoneNumberBlur}
      />
      <div className={styles['phone-number-input-footer']}>
        {meta.error && (
          <div className={styles['phone-number-input-error']}>
            <FieldError name={name}>{meta.error}</FieldError>
          </div>
        )}
      </div>
    </fieldset>
  )
}

export default PhoneNumberInput
