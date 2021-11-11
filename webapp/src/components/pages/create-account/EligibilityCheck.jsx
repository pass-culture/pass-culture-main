import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import InputMask from 'react-input-mask'

import BackLink from '../../layout/Header/BackLink/BackLink'
import Icon from '../../layout/Icon/Icon'
import { checkIfAgeIsEligible, ELIGIBILITY_VALUES } from './domain/checkIfAgeIsEligible'
import {
  checkIfDepartmentIsEligible,
  DEPARTMENT_ELIGIBILITY_VALUES,
} from './domain/checkIfDepartmentIsEligible'
import Eligible from './Eligible/Eligible'
import { AgeEligibleSoon } from './EligibleSoon/AgeEligibleSoon'
import { DepartmentEligibleSoon } from './EligibleSoon/DepartmentEligibleSoon'
import IneligibleOverEighteen from './IneligibleOverEighteen/IneligibleOverEighteen'
import IneligibleUnderEighteen from './IneligibleUnderEighteen/IneligibleUnderEighteen'
import { RecaptchaNotice } from './RecaptchaNotice'
import { useReCaptchaScript } from '../../../utils/recaptcha'
import { campaignTracker } from '../../../tracking/mediaCampaignsTracking'
import IdCheckDisabled from './IdCheckDisabled/IdCheckDisabled'

const EligibilityCheck = ({
  history,
  trackEligibility,
  isIdCheckAvailable,
  wholeFranceOpening,
}) => {
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
    (!wholeFranceOpening && postalCodeInputValue.length < 5) ||
    !dateFormatRegex.test(dateOfBirthInputValue)

  const checkIfDateIsValid = (birthDay, birthMonth, birthYear) => {
    const isDateFormatValid = Date.parse(`${birthYear}-${birthMonth}-${birthDay}`)
    const currentYear = new Date().getFullYear()

    return isDateFormatValid && birthYear <= currentYear && birthYear !== '0000'
  }

  useEffect(() => {
    campaignTracker.eligibilityCheck()

    const script = document.createElement('script')

    script.src = '/ebOneTag.js'

    document.querySelector('body').appendChild(script)
  }, [])

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
      if (ageEligibilityValue === ELIGIBILITY_VALUES.ELIGIBLE) {
        const departmentEligibilityValue =
          wholeFranceOpening || checkIfDepartmentIsEligible(postalCodeInputValue)
            ? DEPARTMENT_ELIGIBILITY_VALUES.ELIGIBLE
            : DEPARTMENT_ELIGIBILITY_VALUES.NOT_ELIGIBLE
        setComponentToRender(departmentEligibilityValue)
      } else {
        setComponentToRender(ageEligibilityValue)
      }
    },
    [dateOfBirthInputValue, postalCodeInputValue, wholeFranceOpening]
  )

  switch (componentToRender) {
    case DEPARTMENT_ELIGIBILITY_VALUES.ELIGIBLE:
      trackEligibility('Eligibilite - OK')

      if (isIdCheckAvailable) {
        return <Eligible />
      } else {
        return <IdCheckDisabled />
      }
    case DEPARTMENT_ELIGIBILITY_VALUES.NOT_ELIGIBLE:
      if (history.location.hash !== '#departement-ineligible') {
        history.replace({
          hash: '#departement-ineligible',
        })
      }
      trackEligibility('Eligibilite - WrongDepartment')
      return (
        <DepartmentEligibleSoon
          birthDate={dateOfBirthInputValue}
          postalCode={postalCodeInputValue}
        />
      )
    case ELIGIBILITY_VALUES.TOO_YOUNG:
      if (history.location.hash !== '#trop-jeune') {
        history.replace({
          hash: '#trop-jeune',
        })
      }
      trackEligibility('Eligibilite - TooYoung')
      return <IneligibleUnderEighteen />
    case ELIGIBILITY_VALUES.TOO_OLD:
      if (history.location.hash !== '#trop-age') {
        history.replace({
          hash: '#trop-age',
        })
      }
      trackEligibility('Eligibilite - TooOld')
      return <IneligibleOverEighteen />
    case ELIGIBILITY_VALUES.SOON:
      trackEligibility('Eligibilite - Soon')
      return (
        <AgeEligibleSoon
          birthDate={dateOfBirthInputValue}
          postalCode={postalCodeInputValue}
        />
      )
    default:
      if (history.location.hash !== '') {
        history.replace({
          hash: '',
        })
      }
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
              {!wholeFranceOpening && (
                <label>
                  {'Quel est ton code postal de résidence ?'}
                  <input
                    aria-label="Renseigne ton code postal de résidence (Exemple : 75017)"
                    autoComplete="postal-code"
                    inputMode="numeric"
                    maxLength="5"
                    onChange={handlePostalCodeInputChange}
                    placeholder="Ex: 75017"
                    required
                    type="text"
                    value={postalCodeInputValue}
                  />
                </label>
              )}
              <label>
                {'Quelle est ta date de naissance ?'}
                <InputMask
                  aria-label="Renseigne ta date de naissance sous la forme JJ/MM/AAAA"
                  autoComplete="bday"
                  className={`date-of-birth-input ${
                    hasAnErrorMessage ? 'date-of-birth-input-error' : ''
                  }`}
                  inputMode="numeric"
                  mask={dateOfBirthInputValue.length > 0 ? '99/99/9999' : null}
                  onChange={handleDOBInputChange}
                  placeholder="JJ/MM/AAAA"
                  required
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

EligibilityCheck.propTypes = {
  history: PropTypes.shape().isRequired,
  isIdCheckAvailable: PropTypes.bool.isRequired,
  trackEligibility: PropTypes.func.isRequired,
  wholeFranceOpening: PropTypes.bool.isRequired,
}

export default EligibilityCheck
