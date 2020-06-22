import React, { useState } from 'react'
import InputMask from 'react-input-mask'

import BackLink from '../../../layout/Header/BackLink/BackLink'

const EligibilityCheck = () => {
  let [postalCodeInputValue, setPostalCodeInputValue] = useState('')
  let [dateOfBirthInputValue, setDateOfBirthInputValue] = useState('')

  let handlePostalCodeInputChange = event => {
    const newValue = event.target.value
    setPostalCodeInputValue(newValue)
  }

  let handleDOBInputChange = event => {
    const newValue = event.target.value
    setDateOfBirthInputValue(newValue)
  }

  let isMissingField = () => {
    return postalCodeInputValue.length < 6 || dateOfBirthInputValue.length < 10
  }

  return (
    <main className="eligibility-check-page">
      <div className="elgbt-header">
        <BackLink backTo="/beta" />
        <span>
          {'Créer un compte'}
        </span>
      </div>
      <form className="elgbt-form">
        <label>
          <span>
            {'Quel est ton code postal de résidence ?'}
          </span>
          <InputMask
            inputMode="numeric"
            mask="99 999"
            maskPlaceholder={null}
            onChange={handlePostalCodeInputChange}
            placeholder="Ex: 75 017"
            value={postalCodeInputValue}
          />
        </label>
        <label>
          <span>
            {'Quelle est ta date de naissance ?'}
          </span>
          <InputMask
            inputMode="numeric"
            mask="99/99/9999"
            maskPlaceholder={null}
            onChange={handleDOBInputChange}
            placeholder="JJ/MM/AAAA"
            value={dateOfBirthInputValue}
          />
        </label>
        <input
          className="elgbt-submit"
          disabled={isMissingField()}
          type="submit"
          value="Vérifier mon éligibilité"
        />
      </form>
    </main>
  )
}

export default EligibilityCheck
