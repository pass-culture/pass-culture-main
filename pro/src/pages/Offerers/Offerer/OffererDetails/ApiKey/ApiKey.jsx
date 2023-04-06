import cn from 'classnames'
import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import useNotification from 'hooks/useNotification'
import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'
import { Banner, Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ENV_WORDING } from 'utils/config'

import styles from './ApiKey.module.scss'

/* @debt duplicated "Gaël: regroup buttons within one component"*/

const ApiKey = ({
  savedApiKeys,
  maxAllowedApiKeys,
  offererId,
  reloadOfferer,
}) => {
  const [newlyGeneratedKeys, setNewlyGeneratedKeys] = useState([])
  const [isGeneratingKey, setIsGeneratingKey] = useState(false)
  const [apiKeyToDelete, setApiKeyToDelete] = useState(null)

  const notification = useNotification()

  const generateApiKey = useCallback(async () => {
    try {
      setIsGeneratingKey(true)
      const generatedApiKey = (await api.generateApiKeyRoute(offererId)).apiKey
      setNewlyGeneratedKeys(previousKeys => [...previousKeys, generatedApiKey])
      notification.success(
        'Votre clé a bien été générée. Attention elle ne sera affichée que quelques instants !'
      )
      setIsGeneratingKey(false)
    } catch {
      notification.error("Une erreur s'est produite, veuillez réessayer")
      setIsGeneratingKey(false)
    }
  }, [offererId, notification])

  function changeApiKeyToDelete(savedApiKey) {
    return () => {
      setApiKeyToDelete(savedApiKey)
    }
  }

  const confirmApiKeyDeletion = useCallback(async () => {
    try {
      await api.deleteApiKey(apiKeyToDelete)
      reloadOfferer(offererId)
    } catch (e) {
      notification.error("Une erreur s'est produite, veuillez réessayer")
    }
    setApiKeyToDelete(null)
  }, [apiKeyToDelete, notification, offererId, reloadOfferer])

  const copyKey = apiKeyToCopy => async () => {
    try {
      await navigator.clipboard.writeText(apiKeyToCopy)
      notification.success('Clé copiée dans le presse-papier !')
    } catch {
      notification.error('Impossible de copier la clé dans le presse-papier')
    }
  }

  const generatedKeysCount = savedApiKeys.length + newlyGeneratedKeys.length
  const isMaxAllowedReached = generatedKeysCount >= maxAllowedApiKeys

  return (
    <div className={cn(styles['section'], styles['api-key'])}>
      <div className={styles['main-list-title']}>
        <h2 className={styles['main-list-title-text']}>Gestion des clés API</h2>
      </div>
      <Banner
        links={[
          {
            href: 'https://www.notion.so/passcultureapp/pass-Culture-Int-grations-techniques-231e16685c9a438b97bdcd7737cdd4d1',
            linkTitle: 'En savoir plus sur les clés API',
          },
        ]}
        type="notification-info"
      />
      <div className={styles['title']}>
        <div className={styles['text']}>
          {'API '}
          {ENV_WORDING}
        </div>
        <div
          className={cn(styles['counter'], {
            [styles['counter--error']]: isMaxAllowedReached,
          })}
        >
          {generatedKeysCount}/{maxAllowedApiKeys}
        </div>
      </div>
      <div className={styles['info']}>
        {"Vous pouvez avoir jusqu'à "}
        {maxAllowedApiKeys}
        {' clé'}
        {maxAllowedApiKeys > 1 ? 's' : ''}
        {' API.'}
      </div>
      <div className={styles['list']}>
        {savedApiKeys.map(savedApiKey => {
          return (
            <div className={styles['item']} key={savedApiKey}>
              <span className={styles['text']}>
                {savedApiKey}
                ********
              </span>
              <Button
                className={styles['action']}
                onClick={changeApiKeyToDelete(savedApiKey)}
                variant={ButtonVariant.TERNARY}
                Icon={TrashIcon}
              >
                supprimer
              </Button>
            </div>
          )
        })}
        {newlyGeneratedKeys.map(newKey => {
          return (
            <div className={styles['item']} key={newKey}>
              <span className={cn(styles['text'], styles['text--new-key'])}>
                {newKey}
              </span>
              <Button
                className={styles['action']}
                onClick={copyKey(newKey)}
                variant={ButtonVariant.PRIMARY}
              >
                Copier
              </Button>
            </div>
          )
        })}
      </div>
      {!!newlyGeneratedKeys.length && (
        <Banner>
          Veuillez copier cette clé et la stocker dans un endroit sûr car vous
          ne pourrez plus la visualiser entièrement ici.
        </Banner>
      )}
      <Button
        className={styles['generate']}
        isLoading={isGeneratingKey}
        variant={ButtonVariant.SECONDARY}
        disabled={isMaxAllowedReached || isGeneratingKey}
        onClick={generateApiKey}
      >
        Générer une clé API
      </Button>
      {!!apiKeyToDelete && (
        <ConfirmDialog
          extraClassNames={styles['api-key-dialog']}
          labelledBy="api-key-deletion-dialog"
          onCancel={changeApiKeyToDelete(null)}
          onConfirm={confirmApiKeyDeletion}
          title="Êtes-vous sûr de vouloir supprimer votre clé API ?"
          confirmText="Confirmer la suppression"
          cancelText="Annuler"
          icon={TrashIcon}
        >
          <div className={styles['explanation']}>
            <p>
              Attention, si vous supprimez cette clé, et qu’aucune autre n’a été
              générée, cela entraînera une rupture du service.
            </p>
            <br />
            <p>Cette action est irréversible.</p>
          </div>
        </ConfirmDialog>
      )}
    </div>
  )
}
ApiKey.propTypes = {
  maxAllowedApiKeys: PropTypes.number.isRequired,
  offererId: PropTypes.number.isRequired,
  reloadOfferer: PropTypes.func.isRequired,
  savedApiKeys: PropTypes.arrayOf(PropTypes.string).isRequired,
}

export default ApiKey
