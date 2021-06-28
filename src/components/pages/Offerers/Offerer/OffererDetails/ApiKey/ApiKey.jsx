import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import Banner from 'components/layout/Banner/Banner'
import { ReactComponent as SpinnerIcon } from 'components/layout/SubmitButton/assets/loader.svg'
import { generateOffererApiKey } from 'repository/pcapi/pcapi'
import { ENV_WORDING } from 'utils/config'

const ApiKey = ({ savedApiKeys, maxAllowedApiKeys, offererId, showNotification }) => {
  const [newlyGeneratedKeys, setNewGeneratedKeys] = useState([])
  const [isGeneratingKey, setIsGeneratingKey] = useState(false)

  const generateApiKey = useCallback(async () => {
    try {
      setIsGeneratingKey(true)
      const generatedApiKey = await generateOffererApiKey(offererId)
      setNewGeneratedKeys(previousKeys => [...previousKeys, generatedApiKey])
      showNotification(
        'success',
        'Votre clé a bien été générée. Attention elle ne sera affichée que quelques instants !'
      )
      setIsGeneratingKey(false)
    } catch {
      showNotification('error', "Une erreur s'est produite, veuillez réessayer")
      setIsGeneratingKey(false)
    }
  }, [offererId, showNotification])

  const copyKey = apiKeyToCopy => async () => {
    try {
      await navigator.clipboard.writeText(apiKeyToCopy)
      showNotification('success', 'Clé copiée dans le presse-papier !')
    } catch {
      showNotification('error', 'Impossible de copier la clé dans le presse-papier')
    }
  }

  const generatedKeysCount = savedApiKeys.length + newlyGeneratedKeys.length
  const isMaxAllowedReached = generatedKeysCount >= maxAllowedApiKeys

  return (
    <div className="section op-content-section api-key">
      <div className="main-list-title">
        <h2 className="main-list-title-text">
          {'Gestion des clés API'}
        </h2>
      </div>
      <Banner
        href="https://www.notion.so/passcultureapp/pass-Culture-Int-grations-techniques-231e16685c9a438b97bdcd7737cdd4d1"
        linkTitle="En savoir plus sur les clés API"
        type="notification-info"
      />
      <div className="title">
        <div className="text">
          {'API '}
          {ENV_WORDING}
        </div>
        <div className={`counter${isMaxAllowedReached ? ' counter--error' : ''}`}>
          {generatedKeysCount}
          {'/'}
          {maxAllowedApiKeys}
        </div>
      </div>
      <div className="info">
        {"Vous pouvez avoir jusqu'à "}
        {maxAllowedApiKeys}
        {' clé'}
        {maxAllowedApiKeys > 1 ? 's' : ''}
        {' API.'}
      </div>
      <div className="list">
        {savedApiKeys.map(savedApiKey => {
          return (
            <div
              className="item"
              key={savedApiKey}
            >
              <span className="text">
                {savedApiKey}
                {'********'}
              </span>
            </div>
          )
        })}
        {newlyGeneratedKeys.map(newKey => {
          return (
            <div
              className="item"
              key={newKey}
            >
              <span className="text text--new-key">
                {newKey}
              </span>
              <button
                className="secondary-button action"
                onClick={copyKey(newKey)}
                type="button"
              >
                {'Copier'}
              </button>
            </div>
          )
        })}
      </div>
      {!!newlyGeneratedKeys.length && (
        <Banner>
          {
            'Veuillez copier cette clé et la stocker dans un endroit sûr car vous ne pourrez plus la visualiser entièrement ici.'
          }
        </Banner>
      )}
      <button
        className={`generate ${
          isGeneratingKey ? 'primary-button submit-button loading-spinner' : 'secondary-button'
        }`}
        disabled={isMaxAllowedReached || isGeneratingKey}
        onClick={generateApiKey}
        type="button"
      >
        {isGeneratingKey ? <SpinnerIcon /> : 'Générer une clé API'}
      </button>
    </div>
  )
}
ApiKey.propTypes = {
  maxAllowedApiKeys: PropTypes.number.isRequired,
  offererId: PropTypes.string.isRequired,
  savedApiKeys: PropTypes.arrayOf(PropTypes.string).isRequired,
  showNotification: PropTypes.func.isRequired,
}

export default ApiKey
