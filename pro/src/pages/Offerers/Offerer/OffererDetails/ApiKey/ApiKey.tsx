import cn from 'classnames'
import { useState } from 'react'

import { api } from 'apiClient/api'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { useNotification } from 'hooks/useNotification'
import strokeTrashIcon from 'icons/stroke-trash.svg'
import { Banner } from 'ui-kit/Banners/Banner/Banner'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { ENV_WORDING } from 'utils/config'

import styles from './ApiKey.module.scss'

interface ApiKeyProps {
  maxAllowedApiKeys: number
  offererId: number
  reloadOfferer: (offererId: number) => Promise<void>
  savedApiKeys: string[]
}

/* @debt duplicated "Gaël: regroup buttons within one component"*/
export const ApiKey = ({
  savedApiKeys,
  maxAllowedApiKeys,
  offererId,
  reloadOfferer,
}: ApiKeyProps) => {
  const [newlyGeneratedKeys, setNewlyGeneratedKeys] = useState<string[]>([])
  const [isGeneratingKey, setIsGeneratingKey] = useState(false)
  const [apiKeyToDelete, setApiKeyToDelete] = useState<string | null>(null)

  const notification = useNotification()

  const generateApiKey = async () => {
    try {
      setIsGeneratingKey(true)
      const generatedApiKey = (await api.generateApiKeyRoute(offererId)).apiKey
      setNewlyGeneratedKeys((previousKeys) => [
        ...previousKeys,
        generatedApiKey,
      ])
      notification.success(
        'Votre clé a bien été générée. Attention elle ne sera affichée que quelques instants !'
      )
      setIsGeneratingKey(false)
    } catch {
      notification.error('Une erreur s’est produite, veuillez réessayer')
      setIsGeneratingKey(false)
    }
  }

  const confirmApiKeyDeletion = async () => {
    if (!apiKeyToDelete) {
      return
    }

    try {
      await api.deleteApiKey(apiKeyToDelete)
      await reloadOfferer(offererId)
    } catch (e) {
      notification.error('Une erreur s’est produite, veuillez réessayer')
    }

    setApiKeyToDelete(null)
  }

  const copyKey = (apiKeyToCopy: string) => async () => {
    try {
      await navigator.clipboard.writeText(apiKeyToCopy)
      notification.success('Clé copiée dans le presse-papier !')
    } catch {
      notification.error('Impossible de copier la clé dans le presse-papier')
    }
  }

  const deduplicateSavedKeyFromNewOnes = savedApiKeys.filter(
    (savedKey) =>
      !newlyGeneratedKeys.some((newKey) => newKey.startsWith(savedKey))
  )
  const generatedKeysCount =
    deduplicateSavedKeyFromNewOnes.length + newlyGeneratedKeys.length
  const isMaxAllowedReached = generatedKeysCount >= maxAllowedApiKeys

  return (
    <div className={cn(styles['section'], styles['api-key'])}>
      <h2 className={styles['main-list-title']}>Gestion des clés API</h2>

      <Banner
        links={[
          {
            href: 'https://aide.passculture.app/hc/fr/articles/4411999022225--Acteurs-Culturels-Comment-obtenir-sa-clé-API-sur-son-compte-pass-Culture-Pro',
            label: 'En savoir plus sur les clés API',
            isExternal: true,
          },
        ]}
        type="notification-info"
      />

      <div className={styles['title']}>
        {'API '}
        {ENV_WORDING}
        <span className={isMaxAllowedReached ? styles['counter-error'] : ''}>
          {' '}
          {generatedKeysCount}/{maxAllowedApiKeys}
        </span>
      </div>

      <div className={styles['info']}>
        {"Vous pouvez avoir jusqu'à "}
        {maxAllowedApiKeys}
        {' clé'}
        {maxAllowedApiKeys > 1 ? 's' : ''}
        {' API.'}
      </div>

      {(savedApiKeys.length > 0 || newlyGeneratedKeys.length > 0) && (
        <div className={styles['list']}>
          {deduplicateSavedKeyFromNewOnes.map((savedApiKey) => {
            return (
              <div className={styles['item']} key={savedApiKey}>
                <span className={styles['text']}>
                  {savedApiKey}
                  ********
                </span>
                <Button
                  className={styles['action']}
                  onClick={() => setApiKeyToDelete(savedApiKey)}
                  variant={ButtonVariant.TERNARY}
                  icon={strokeTrashIcon}
                >
                  supprimer
                </Button>
              </div>
            )
          })}

          {newlyGeneratedKeys.map((newKey) => {
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
      )}

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

      {apiKeyToDelete !== null && (
        <ConfirmDialog
          extraClassNames={styles['api-key-dialog']}
          onCancel={() => setApiKeyToDelete(null)}
          onConfirm={confirmApiKeyDeletion}
          title="Êtes-vous sûr de vouloir supprimer votre clé API ?"
          confirmText="Confirmer la suppression"
          cancelText="Annuler"
          icon={strokeTrashIcon}
        >
          <div>
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
