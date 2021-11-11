/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'

const Credit = ({ credit, setCredit, setStep, step }) => {
  const [inputCredit, setInputCredit] = useState(credit)

  const updateCredit = useCallback(event => {
    setInputCredit(event.target.value)
  }, [])

  const previousStep = useCallback(() => {
    setStep(step - 1)
  }, [setStep, step])

  const nextStep = useCallback(() => {
    setCredit(inputCredit)
    setStep(step + 1)
  }, [step, inputCredit, setCredit, setStep])

  return (
    <>
      <div className="tnd-subtitle">
        Crédit image et droits d’utilisation
      </div>

      <TextInput
        countCharacters
        label="Crédit image"
        maxLength={255}
        name="thumbnail-credit"
        onChange={updateCredit}
        placeholder="Photographe..."
        required={false}
        subLabel="Optionnel"
        type="text"
        value={inputCredit}
      />

      <div className="tnc-explanations">
        En utilisant ce contenu, je certifie que je suis propriétaire ou que je dispose des autorisations nécessaires pour l’utilisation de celui-ci
      </div>

      <div className="tnd-actions">
        <button
          className="secondary-button"
          onClick={previousStep}
          title="Retour"
          type="button"
        >
          Retour
        </button>
        <button
          className="primary-button"
          onClick={nextStep}
          title="Suivant"
          type="button"
        >
          Suivant
        </button>
      </div>
    </>
  )
}

Credit.propTypes = {
  credit: PropTypes.string.isRequired,
  setCredit: PropTypes.func.isRequired,
  setStep: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
}

export default Credit
