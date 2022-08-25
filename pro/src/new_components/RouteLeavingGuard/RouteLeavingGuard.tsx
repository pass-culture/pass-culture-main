import React, { ReactNode, useCallback, useState } from 'react'
import { Redirect, useHistory, Prompt } from 'react-router-dom'

import ConfirmDialog from 'new_components/ConfirmDialog'

export interface IShouldBlockNavigationReturnValue {
  redirectPath?: string | null
  shouldBlock: boolean
}
export interface IRouteLeavingGuardProps {
  children: ReactNode | ReactNode[]
  extraClassNames?: string
  shouldBlockNavigation: (
    location: Location
  ) => IShouldBlockNavigationReturnValue
  when: boolean
  dialogTitle: string
}

const RouteLeavingGuard = ({
  children,
  extraClassNames = '',
  shouldBlockNavigation,
  when,
  dialogTitle,
}: IRouteLeavingGuardProps): JSX.Element => {
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [lastLocation, setLastLocation] = useState('')
  const [isConfirmedNavigation, setIsConfirmedNavigation] = useState(false)
  const history = useHistory()

  const closeModal = useCallback(() => {
    setIsModalVisible(false)
  }, [])

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

  const handleConfirmNavigationClick = useCallback(() => {
    setIsModalVisible(false)
    setIsConfirmedNavigation(true)
  }, [])

  return isConfirmedNavigation && lastLocation ? (
    <Redirect push to={lastLocation} />
  ) : (
    <>
      <Prompt message={handleBlockedNavigation} when={when} />
      {isModalVisible && (
        <ConfirmDialog
          extraClassNames={extraClassNames}
          onCancel={closeModal}
          onConfirm={handleConfirmNavigationClick}
          title={dialogTitle}
          confirmText="Quitter"
          cancelText="Annuler"
        >
          {children}
        </ConfirmDialog>
      )}
    </>
  )
}

export default RouteLeavingGuard
