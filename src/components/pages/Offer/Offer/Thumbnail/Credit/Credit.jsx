import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import TextInput from 'components/layout/inputs/TextInput/TextInput'

const Credit = ({ setCredit, setStep }) => {
  const [credit, setInputCredit] = useState('')

  const updateCredit = useCallback(event => {
    setInputCredit(event.target.value)
  }, [])

  const previousStep = useCallback(() => {
    setStep(1)
  }, [setStep])

  return (
    <>
      <div className="tnd-subtitle">
        {'Crédit image et droits d’utilisation'}
      </div>

      <TextInput
        label="Crédit image"
        maxLength={255}
        name="thumbnail-credit"
        onChange={updateCredit}
        placeholder="Photographe..."
        required={false}
        subLabel="Optionnel"
        type="text"
        value={credit}
      />

      <div className="tnc-explanations">
        {
          'En utilisant ce contenu, je certifie que je suis propriétaire ou que je dispose des autorisations nécessaires pour l’utilisation de celui-ci'
        }
      </div>

      <div className="tnd-actions">
        <button
          className="secondary-button"
          onClick={previousStep}
          title="Retour"
          type="button"
        >
          {'Retour'}
        </button>
        <button
          className="primary-button"
          onClick={setCredit}
          title="Suivant"
          type="button"
        >
          {'Suivant'}
        </button>
      </div>
    </>
  )
}

Credit.propTypes = {
  setCredit: PropTypes.func.isRequired,
  setStep: PropTypes.func.isRequired,
}

export default Credit
