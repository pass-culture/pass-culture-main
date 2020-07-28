import React, { useCallback, useState } from 'react'
import InputMask from 'react-input-mask'

import BackLink from '../../layout/Header/BackLink/BackLink'
import Icon from '../../layout/Icon/Icon'
import { checkIfAgeIsEligible, ELIGIBILITY_VALUES } from './domain/checkIfAgeIsEligible'
import { checkIfDepartmentIsEligible } from './domain/checkIfDepartmentIsEligible'
import Eligible from './Eligible/Eligible'
import { AgeEligibleSoon } from './EligibleSoon/AgeEligibleSoon'
import { DepartmentEligibleSoon } from './EligibleSoon/DepartmentEligibleSoon'
import IneligibleOverEighteen from './IneligibleOverEighteen/IneligibleOverEighteen'
import IneligibleUnderEighteen from './IneligibleUnderEighteen/IneligibleUnderEighteen'
import { RecaptchaNotice } from './RecaptchaNotice'
import { useReCaptchaScript } from './utils/recaptcha'

const EligibilityCheck = () => {
  useReCaptchaScript()
  const [postalCodeInputValue, setPostalCodeInputValue] = useState('')
  const [dateOfBirthInputValue, setDateOfBirthInputValue] = useState('')
  const [componentToRender, setComponentToRender] = useState('')
  const [hasAnErrorMessage, setHasAnErrorMessage] = useState(false)

  const keepNumbersOnly = string => string.replace(/[^0-9]/g, '')

  const handlePostalCodeInputChange = useCallback(event => {
    let newValue = keepNumbersOnly(event.target.value)
    setPostalCodeInputValue(newValue)
  }, [])

  const handleDOBInputChange = useCallback(event => {
    const newValue = event.target.value
    setDateOfBirthInputValue(newValue)
    setHasAnErrorMessage(false)
  }, [])

  const dateFormatRegex = RegExp('[0-9]{2}/[0-9]{2}/[0-9]{4}', 'g')
  const isMissingField =
    postalCodeInputValue.length < 5 || !dateFormatRegex.test(dateOfBirthInputValue)

  const checkIfDateIsValid = (birthDay, birthMonth, birthYear) => {
    const isDateFormatValid = Date.parse(`${birthYear}-${birthMonth}-${birthDay}`)
    const currentYear = new Date().getFullYear()

    return isDateFormatValid && birthYear <= currentYear && birthYear !== '0000'
  }

  const handleSubmit = useCallback(
    event => {
      event.preventDefault()
      const splittedBirthDate = dateOfBirthInputValue.split('/')
      const birthDay = splittedBirthDate[0]
      const birthMonth = splittedBirthDate[1]
      const birthYear = splittedBirthDate[2]

      if (!checkIfDateIsValid(birthDay, birthMonth, birthYear)) {
        return setHasAnErrorMessage(true)
      }

      setHasAnErrorMessage(false)
      const ageEligibilityValue = checkIfAgeIsEligible(dateOfBirthInputValue)
      setComponentToRender(ageEligibilityValue)
    },
    [dateOfBirthInputValue]
  )

  switch (componentToRender) {
    case ELIGIBILITY_VALUES.ELIGIBLE:
      return checkIfDepartmentIsEligible(postalCodeInputValue) ? (
        <Eligible />
      ) : (
        <DepartmentEligibleSoon
          birthDate={dateOfBirthInputValue}
          postalCode={postalCodeInputValue}
        />
      )
    case ELIGIBILITY_VALUES.TOO_YOUNG:
      return <IneligibleUnderEighteen />
    case ELIGIBILITY_VALUES.TOO_OLD:
      return <IneligibleOverEighteen />
    case ELIGIBILITY_VALUES.SOON:
      return (<AgeEligibleSoon
        birthDate={dateOfBirthInputValue}
        postalCode={postalCodeInputValue}
              />)
    default:
      return (
        <main className="eligibility-check-page">
          <BackLink backTo="/beta" />
          <span className="eligibility-title">
            {'Créer un compte'}
          </span>
          <form
            className="eligibility-form"
            onSubmit={handleSubmit}
          >
            <div>
              <label>
                {'Quel est ton code postal de résidence ?'}
                <input
                  inputMode="numeric"
                  maxLength="5"
                  onChange={handlePostalCodeInputChange}
                  placeholder="Ex: 75017"
                  type="text"
                  value={postalCodeInputValue}
                />
              </label>
              <label>
                {'Quelle est ta date de naissance ?'}
                <InputMask
                  className={`date-of-birth-input ${
                    hasAnErrorMessage ? 'date-of-birth-input-error' : ''
                  }`}
                  inputMode="numeric"
                  mask="99/99/9999"
                  onChange={handleDOBInputChange}
                  placeholder="JJ/MM/AAAA"
                  value={dateOfBirthInputValue}
                />
                {hasAnErrorMessage && (
                  <div className="dob-field-error">
                    <Icon svg="ico-error" />
                    <pre>
                      {'Le format de la date est incorrect.'}
                    </pre>
                  </div>
                )}
              </label>
            </div>
            <div>
              <RecaptchaNotice />
              <input
                className="eligibility-submit"
                disabled={isMissingField || hasAnErrorMessage}
                type="submit"
                value="Vérifier mon éligibilité"
              />
            </div>
          </form>
        </main>
      )
  }
}

export default EligibilityCheck
