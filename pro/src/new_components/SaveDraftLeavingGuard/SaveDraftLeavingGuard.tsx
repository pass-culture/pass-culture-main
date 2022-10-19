import React, { useCallback, useEffect, useState } from 'react'
import { Redirect, useHistory, Prompt } from 'react-router-dom'

import ConfirmDialog from 'new_components/ConfirmDialog'

export interface IShouldBlockNavigationReturnValue {
  redirectPath?: string | null
  shouldBlock: boolean
}
export interface ISaveDraftLeavingGuardProps {
  shouldBlockNavigation: (
    location: Location
  ) => IShouldBlockNavigationReturnValue
  when: boolean
  onSubmit: () => void
  isValid: () => Promise<boolean>
}

const SaveDraftLeavingGuard = ({
  shouldBlockNavigation,
  when,
  onSubmit,
  isValid,
}: ISaveDraftLeavingGuardProps): JSX.Element => {
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [lastLocation, setLastLocation] = useState('')
  const [isConfirmedNavigation, setIsConfirmedNavigation] = useState(false)
  const [isFormValid, setIsFormValid] = useState(false)
  const history = useHistory()

  const handleBlockedNavigation = useCallback(
    (nextLocation: any) => {
      const { redirectPath, shouldBlock } = shouldBlockNavigation(nextLocation)
      setLastLocation(redirectPath ? redirectPath : nextLocation)
      if (!isConfirmedNavigation && shouldBlock) {
        setIsModalVisible(true)
        return false
      }
      if (redirectPath) {
        history.push({ pathname: redirectPath })
        return false
      }

      return true
    },
    [isConfirmedNavigation, history, shouldBlockNavigation]
  )

  const handleConfirmCloseClick = useCallback(() => {
    setIsModalVisible(false)
    setIsConfirmedNavigation(true)
  }, [])

  const handleCancelLeave = useCallback(() => {
    setIsModalVisible(false)
    setIsConfirmedNavigation(false)
  }, [])

  const handleSaveDraft = () => {
    setIsModalVisible(false)
    onSubmit()
  }
  useEffect(() => {
    const isFormValid = async () => {
      if (await isValid()) {
        setIsFormValid(true)
      }
    }
    if (isModalVisible) isFormValid()
  }, [isModalVisible])

  return isConfirmedNavigation && lastLocation ? (
    <Redirect push to={lastLocation} />
  ) : (
    <>
      <Prompt message={handleBlockedNavigation} when={when} />
      {isModalVisible &&
        (isFormValid ? (
          <ConfirmDialog
            onCancel={handleConfirmCloseClick}
            onConfirm={handleSaveDraft}
            title="Souhaitez-vous enregistrer cette offre en brouillon avant de quitter ?"
            confirmText="Enregistrer un brouillon et quitter"
            cancelText="Quitter sans enregistrer"
          >
            <p>
              Vous pourrez la retrouver dans la liste de vos offres pour la
              compléter et la publier plus tard.
            </p>
          </ConfirmDialog>
        ) : (
          <ConfirmDialog
            onCancel={handleCancelLeave}
            onConfirm={handleConfirmCloseClick}
            title="Souhaitez-vous quitter la création d’offre ?"
            confirmText="Quitter"
            cancelText="Annuler"
          >
            <p>
              Votre offre ne sera pas sauvegardée et toutes les informations
              seront perdues.
            </p>
          </ConfirmDialog>
        ))}
    </>
  )
}

export default SaveDraftLeavingGuard
