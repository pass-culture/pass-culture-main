import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import BackLink from '../../../layout/Header/BackLink/BackLink'
import { checkIfAgeIsEligible } from '../domain/checkIfAgeIsEligible'
import { checkIfDepartmentIsEligible } from '../domain/checkIfDepartmentIsEligible'
import { eligibilityPaths } from './eligibilityPaths'

const EligibilityCheck = ({ historyPush, pathname }) => {
  const [postalCodeInputValue, setPostalCodeInputValue] = useState('')
  const [dateOfBirthInputValue, setDateOfBirthInputValue] = useState('')

  const getCurrentPathName = () => {
    const currentPathname = pathname

    return currentPathname.slice(-1) !== '/' ? currentPathname + '/' : currentPathname
  }

  const addSlashToBirthDate = birthDate => {
    const fullDateLength = 8
    const dayDateLength = 2
    const monthDateLength = 4
    if (birthDate.length < dayDateLength) {
      return birthDate
    }
    if (birthDate.length >= dayDateLength && birthDate.length < monthDateLength) {
      return birthDate[0] + birthDate[1] + '/' + birthDate.slice(2)
    }
    if (birthDate.length >= monthDateLength && birthDate.length <= fullDateLength) {
      return (
        birthDate[0] + birthDate[1] + '/' + birthDate[2] + birthDate[3] + '/' + birthDate.slice(4)
      )
    }
  }

  const keepNumbersOnly = string => string.replace(/[^0-9]/g, '')

  const sanitizeBirthDateInputValue = event => {
    const previousValueLastChar = dateOfBirthInputValue.slice(-1)
    let newValue = keepNumbersOnly(event.target.value)
    if (previousValueLastChar === '/' && event.nativeEvent.inputType === 'deleteContentBackward') {
      newValue = dateOfBirthInputValue.slice(0, -2)
    }

    return newValue.replace(/\//g, '')
  }

  const handlePostalCodeInputChange = useCallback(
    event => {
      let newValue = keepNumbersOnly(event.target.value)
      setPostalCodeInputValue(newValue)
    },
    [postalCodeInputValue]
  )

  const handleBirthDateChange = useCallback(
    event => {
      const sanitizedNewValue = sanitizeBirthDateInputValue(event)
      setDateOfBirthInputValue(addSlashToBirthDate(sanitizedNewValue))
    },
    [dateOfBirthInputValue]
  )

  const handleSubmit = useCallback(
    event => {
      event.preventDefault()
      const currentPathName = getCurrentPathName()
      const splittedBirthDate = dateOfBirthInputValue.split('/')
      const birthDay = splittedBirthDate[0]
      const birthMonth = splittedBirthDate[1]
      const birthYear = splittedBirthDate[2]
      const currentYear = new Date().getFullYear()
      const isDateFormatValid = Date.parse(`${birthDay}-${birthMonth}-${birthDay}`)

      if (!isDateFormatValid || birthYear > currentYear) {
        return historyPush('/verification-eligibilite/pas-eligible')
      }

      const ageEligibilityValue = checkIfAgeIsEligible(dateOfBirthInputValue)

      if (ageEligibilityValue === 'eligible') {
        const isDepartmentEligible = checkIfDepartmentIsEligible(postalCodeInputValue)

        isDepartmentEligible
          ? historyPush(currentPathName + eligibilityPaths[ageEligibilityValue])
          : historyPush(currentPathName + 'departement-non-eligible')
      } else {
        historyPush(currentPathName + eligibilityPaths[ageEligibilityValue])
      }
    },
    [postalCodeInputValue, dateOfBirthInputValue]
  )

  const isMissingField = postalCodeInputValue.length < 5 || dateOfBirthInputValue.length < 10

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
              value={postalCodeInputValue}
            />
          </label>
          <label>
            {'Quelle est ta date de naissance ?'}
            <input
              inputMode="numeric"
              maxLength="10"
              onChange={handleBirthDateChange}
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
  historyPush: PropTypes.func.isRequired,
  pathname: PropTypes.string.isRequired,
}

export default EligibilityCheck
