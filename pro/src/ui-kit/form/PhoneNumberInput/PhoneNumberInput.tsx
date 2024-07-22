import { useField } from 'formik'
import { parsePhoneNumberFromString } from 'libphonenumber-js'
import type { CountryCode } from 'libphonenumber-js'
import React, { ChangeEvent, FocusEvent, useEffect, useState } from 'react'

import { BaseInput } from '../shared/BaseInput/BaseInput'
import { FieldError } from '../shared/FieldError/FieldError'
import { FieldLayoutBaseProps } from '../shared/FieldLayout/FieldLayout'

import { CountryCodeSelect } from './CodeCountrySelect/CountryCodeSelect'
import { PHONE_CODE_COUNTRY_CODE_OPTIONS, PLACEHOLDER_MAP } from './constants'
import styles from './PhoneNumberInput.module.scss'
import { getPhoneNumberInputAndCountryCode } from './utils/getPhoneNumberInputAndCountryCode'

type PhoneNumberInputProps = FieldLayoutBaseProps & {
  disabled?: boolean
  maxLength?: number
}

export const PhoneNumberInput = ({
  name,
  label,
  disabled,
  isOptional = false,
  maxLength = 25,
}: PhoneNumberInputProps) => {
  const [field, meta, helpers] = useField({ name })

  const [countryCode, setCountryCode] = useState<CountryCode>(
    PHONE_CODE_COUNTRY_CODE_OPTIONS[0]!.value
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

    // save formatted phone number i.e +33639980101 even if user types 0639980101 or 639980101
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
      // input optional -> if optional we want to value formik field with incorrect phone number to raise error on form validation
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
      <label htmlFor="countryCode" className="visually-hidden">
        Indicatif téléphonique
      </label>
      <CountryCodeSelect
        disabled={Boolean(disabled)}
        options={PHONE_CODE_COUNTRY_CODE_OPTIONS}
        className={styles['country-code-select']}
        value={countryCode}
        onChange={onPhoneCodeChange}
      />

      <label htmlFor={name} className="visually-hidden">
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
        autoComplete="tel-national"
        maxLength={maxLength}
      />
      <div className={styles['phone-number-input-footer']}>
        {meta.error && meta.touched && (
          <div className={styles['phone-number-input-error']}>
            <FieldError name={name}>{meta.error}</FieldError>
          </div>
        )}
      </div>
    </fieldset>
  )
}
