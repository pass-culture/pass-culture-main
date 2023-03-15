import React, { ReactNode, useCallback, useState } from 'react'
import { Redirect, Prompt } from 'react-router-dom'
import { useNavigate } from 'react-router-dom-v5-compat'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'

export interface IShouldBlockNavigationReturnValue {
  redirectPath?: string | null
  shouldBlock: boolean
}

export interface IRouteLeavingGuardProps {
  children?: ReactNode | ReactNode[]
  extraClassNames?: string
  shouldBlockNavigation: (
    location: Location
  ) => IShouldBlockNavigationReturnValue
  when: boolean
  dialogTitle: string
  tracking?: (p: string) => void
  rightButton?: string
  leftButton?: string
  // This is a weird behavior that should be unified at a UX level
  // the modal should follow the same behavior
  closeModalOnRightButton?: boolean
}

const RouteLeavingGuard = ({
  children,
  extraClassNames = '',
  shouldBlockNavigation,
  when,
  dialogTitle,
  tracking,
  rightButton = 'Quitter',
  leftButton = 'Annuler',
  closeModalOnRightButton = false,
}: IRouteLeavingGuardProps): JSX.Element => {
  const [isModalVisible, setIsModalVisible] = useState(false)
  // FIX ME no any
  const [nextLocation, setNextLocation] = useState<any>('')
  const [isConfirmedNavigation, setIsConfirmedNavigation] = useState(false)
  const navigate = useNavigate()

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
        navigate(redirectPath)
        return false
      }
      return true
    },
    [isConfirmedNavigation, navigate, shouldBlockNavigation]
  )

  const closeModal = () => {
    setIsModalVisible(false)
  }

  const confirmNavigation = () => {
    setIsModalVisible(false)
    setIsConfirmedNavigation(true)

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
          leftButtonAction={
            closeModalOnRightButton ? confirmNavigation : closeModal
          }
          onConfirm={closeModalOnRightButton ? closeModal : confirmNavigation}
          title={dialogTitle}
          confirmText={rightButton}
          cancelText={leftButton}
        >
          {children}
        </ConfirmDialog>
      )}
    </>
  )
}

export default RouteLeavingGuard
