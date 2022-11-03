import { useField } from 'formik'
import { parsePhoneNumberFromString } from 'libphonenumber-js'
import type { CountryCode } from 'libphonenumber-js'
import React, { ChangeEvent, FocusEvent, useState } from 'react'

import { BaseInput, FieldLayout } from '../shared'

import CodeCountrySelect from './CodeCountrySelect/CountryCodeSelect'
import { PHONE_CODE_COUNTRY_CODE_OPTIONS, PLACEHOLDER_MAP } from './constants'
import styles from './PhoneNumberInput.module.scss'
import { getPhoneNumberInputAndCountryCode } from './utils/getPhoneNumberInputAndCountryCode'

export interface PhoneNumberInputProps {
  name: string
  disabled?: boolean
}

const PhoneNumberInput = ({ name, disabled }: PhoneNumberInputProps) => {
  const [field, meta, helpers] = useField({ name })

  const { inputValue, countryCode: computedCountryCode } =
    getPhoneNumberInputAndCountryCode(field.value)

  const [countryCode, setCountryCode] =
    useState<CountryCode>(computedCountryCode)
  const [phoneInutValue, setPhoneInputValue] = useState<string>(inputValue)

  const validatePhoneNumber = (phoneNumberInputValue: string) => {
    const phoneNumber = parsePhoneNumberFromString(
      phoneNumberInputValue,
      countryCode
    )

    // save formatted phone number i.e +33639980101 even if user types 0639980101 or 639980101
    helpers.setValue(phoneNumber?.number, false)
    setPhoneInputValue(phoneNumberInputValue)

    if (!phoneNumber || !phoneNumber.isValid()) {
      helpers.setError('Veuillez entrer un numéro de téléphone valide')
    } else {
      helpers.setError(undefined)
    }
  }

  const onPhoneNumberChange = (event: ChangeEvent<HTMLInputElement>) => {
    const phoneNumberInputValue = event.target.value
    validatePhoneNumber(phoneNumberInputValue)
  }

  const onPhoneCodeChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setCountryCode(e.target.value as CountryCode)
  }

  const onPhoneNumberBlur = (event: FocusEvent<HTMLInputElement>) => {
    if (!meta.touched) {
      helpers.setTouched(true, false)
    }

    validatePhoneNumber(event.target.value)
  }

  return (
    <FieldLayout
      label="Téléphone"
      name={name}
      showError={meta.touched && !!meta.error}
      error={meta.error}
    >
      <div className={styles['phone-number-input-wrapper']}>
        <CodeCountrySelect
          disabled={Boolean(disabled)}
          options={PHONE_CODE_COUNTRY_CODE_OPTIONS}
          className={styles['country-code-select']}
          value={countryCode}
          onChange={onPhoneCodeChange}
        />

        <BaseInput
          disabled={disabled}
          hasError={meta.touched && !!meta.error}
          placeholder={PLACEHOLDER_MAP[countryCode]}
          type="text"
          name={name}
          value={phoneInutValue}
          onChange={onPhoneNumberChange}
          className={styles['phone-number-input']}
          onBlur={onPhoneNumberBlur}
        />
      </div>
    </FieldLayout>
  )
}

export default PhoneNumberInput
