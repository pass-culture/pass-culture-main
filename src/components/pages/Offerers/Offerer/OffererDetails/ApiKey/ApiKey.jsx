/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import Banner from 'components/layout/Banner/Banner'
import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import Icon from 'components/layout/Icon'
import { deleteOffererApiKey, generateOffererApiKey } from 'repository/pcapi/pcapi'
/* @debt duplicated "Gaël: delete icon import and regroup buttons within one component"*/
import { ReactComponent as SpinnerIcon } from 'ui-kit/SubmitButton/assets/loader.svg'
import { ENV_WORDING } from 'utils/config'

import { ReactComponent as DeleteSvg } from './assets/illus-delete.svg'

const ApiKey = ({
  savedApiKeys,
  maxAllowedApiKeys,
  offererId,
  showNotification,
  loadOffererById,
}) => {
  const [newlyGeneratedKeys, setNewGeneratedKeys] = useState([])
  const [isGeneratingKey, setIsGeneratingKey] = useState(false)
  const [apiKeyToDelete, setApiKeyToDelete] = useState(null)

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

  function changeApiKeyToDelete(savedApiKey) {
    return () => {
      setApiKeyToDelete(savedApiKey)
    }
  }

  const confirmApiKeyDeletion = useCallback(async () => {
    try {
      await deleteOffererApiKey(apiKeyToDelete)
      loadOffererById(offererId)
    } catch (e) {
      showNotification('error', "Une erreur s'est produite, veuillez réessayer")
    }
    setApiKeyToDelete(null)
  }, [apiKeyToDelete, loadOffererById, showNotification, offererId])

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
          Gestion des clés API
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
          /
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
                ********
              </span>
              <button
                className="action  tertiary-button with-icon"
                onClick={changeApiKeyToDelete(savedApiKey)}
                type="button"
              >
                <Icon svg="ico-trash" />
                <span>
                  supprimer
                </span>
              </button>
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
                className="primary-button action"
                onClick={copyKey(newKey)}
                type="button"
              >
                Copier
              </button>
            </div>
          )
        })}
      </div>
      {!!newlyGeneratedKeys.length && (
        <Banner>
          Veuillez copier cette clé et la stocker dans un endroit sûr car vous ne pourrez plus la
          visualiser entièrement ici.
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
      {!!apiKeyToDelete && (
        <DialogBox
          extraClassNames="api-key-dialog"
          labelledBy="api-key-deletion-dialog"
          onDismiss={changeApiKeyToDelete(null)}
        >
          <DeleteSvg />
          <div className="title">
            Êtes-vous sûr de vouloir supprimer votre clé API ?
          </div>
          <div className="explanation">
            <p>
              Attention, si vous supprimez cette clé, et qu’aucune autre n’a été générée, cela
              entraînera une rupture du service.
            </p>
            <br />
            <p>
              Cette action est irréversible.
            </p>
          </div>
          <div className="actions">
            <button
              className="secondary-button"
              onClick={changeApiKeyToDelete(null)}
              type="button"
            >
              Annuler
            </button>
            <button
              className="primary-button confirm"
              onClick={confirmApiKeyDeletion}
              type="button"
            >
              Confirmer la suppression
            </button>
          </div>
        </DialogBox>
      )}
    </div>
  )
}
ApiKey.propTypes = {
  loadOffererById: PropTypes.func.isRequired,
  maxAllowedApiKeys: PropTypes.number.isRequired,
  offererId: PropTypes.string.isRequired,
  savedApiKeys: PropTypes.arrayOf(PropTypes.string).isRequired,
  showNotification: PropTypes.func.isRequired,
}

export default ApiKey
