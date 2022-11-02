import React, { ReactNode, useCallback, useState } from 'react'
import { Redirect, useHistory, Prompt } from 'react-router-dom'

import { ConfirmDialog } from 'new_components/ConfirmDialog'

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
  tracking?: (p: string) => void
}

const RouteLeavingGuard = ({
  children,
  extraClassNames = '',
  shouldBlockNavigation,
  when,
  dialogTitle,
  tracking,
}: IRouteLeavingGuardProps): JSX.Element => {
  const [isModalVisible, setIsModalVisible] = useState(false)
  // @ts-ignore next FIX ME no any
  const [nextLocation, setNextLocation] = useState<any>('')
  const [isConfirmedNavigation, setIsConfirmedNavigation] = useState(false)
  const history = useHistory()

  const closeModal = useCallback(() => {
    setIsModalVisible(false)
  }, [])

  const handleBlockedNavigation = useCallback(
    (chosenLocation: any) => {
      const { redirectPath, shouldBlock } =
        shouldBlockNavigation(chosenLocation)
      setNextLocation(redirectPath ? redirectPath : chosenLocation)
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

  if (isConfirmedNavigation && nextLocation) {
    tracking &&
      tracking(
        Object.keys(nextLocation).includes('pathname')
          ? nextLocation.pathname
          : nextLocation
      )
  }

  return isConfirmedNavigation && nextLocation ? (
    <Redirect push to={nextLocation} />
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
