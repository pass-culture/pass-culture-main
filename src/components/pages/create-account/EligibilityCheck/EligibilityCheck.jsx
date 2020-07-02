import React, { useCallback, useState } from 'react'
import InputMask from 'react-input-mask'
import PropTypes from 'prop-types'

import BackLink from '../../../layout/Header/BackLink/BackLink'
import { checkIfDepartmentIsEligible } from '../domain/checkIfDepartmentIsEligible'
import { checkIfAgeIsEligible } from '../domain/checkIfAgeIsEligible'
import { eligibilityPaths } from './eligibilityPaths'

const EligibilityCheck = ({ history }) => {
  const [postalCodeInputValue, setPostalCodeInputValue] = useState('')
  const [dateOfBirthInputValue, setDateOfBirthInputValue] = useState('')

  const handlePostalCodeInputChange = useCallback(event => {
    const newValue = event.target.value
    setPostalCodeInputValue(newValue)
  }, [])

  const handleDOBInputChange = useCallback(event => {
    const newValue = event.target.value
    setDateOfBirthInputValue(newValue)
  }, [])

  const isMissingField = postalCodeInputValue.length < 5 || dateOfBirthInputValue.length < 10

  const handleSubmit = useCallback(
    event => {
      event.preventDefault()
      const currentPathName = history.location.pathname
      const splittedBirthDate = dateOfBirthInputValue.split('/')
      const birthDay = splittedBirthDate[0]
      const birthMonth = splittedBirthDate[1]
      const birthYear = splittedBirthDate[2]
      const currentYear = new Date().getFullYear()
      const isDateFormatValid = Date.parse(`${birthDay}-${birthMonth}-${birthDay}`)

      if (!isDateFormatValid || birthYear > currentYear) {
        return history.push('/verification-eligibilite/pas-eligible')
      }

      const ageEligibilityValue = checkIfAgeIsEligible(dateOfBirthInputValue)

      if (ageEligibilityValue === 'eligible') {
        const isDepartmentEligible = checkIfDepartmentIsEligible(postalCodeInputValue)

        isDepartmentEligible
          ? history.push(currentPathName + eligibilityPaths[ageEligibilityValue])
          : history.push(currentPathName + 'departement-non-eligible')
      } else {
        history.push(currentPathName + eligibilityPaths[ageEligibilityValue])
      }
    },
    [postalCodeInputValue, dateOfBirthInputValue]
  )

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
            <InputMask
              inputMode="numeric"
              mask="99999"
              maskPlaceholder={null}
              onChange={handlePostalCodeInputChange}
              placeholder="Ex: 75017"
              value={postalCodeInputValue}
            />
          </label>
          <label>
            {'Quelle est ta date de naissance ?'}
            <InputMask
              inputMode="numeric"
              mask="99/99/9999"
              maskPlaceholder={null}
              onChange={handleDOBInputChange}
              placeholder="JJ/MM/AAAA"
              value={dateOfBirthInputValue}
            />
          </label>
        </div>
        <input
          className="eligibility-submit"
          disabled={isMissingField}
          type="submit"
          value="Vérifier mon éligibilité"
        />
      </form>
    </main>
  )
}

EligibilityCheck.propTypes = {
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
    location: PropTypes.shape({
      pathname: PropTypes.string.isRequired,
    }).isRequired,
  }).isRequired,
}

export default EligibilityCheck
