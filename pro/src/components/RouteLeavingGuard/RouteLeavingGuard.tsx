import React, { ReactNode, useCallback, useState } from 'react'
import { Redirect, useHistory, Prompt } from 'react-router-dom'

import ConfirmDialog from 'components/ConfirmDialog'

export interface IShouldBlockNavigationReturnValue {
  redirectPath?: string | null
  shouldBlock: boolean
}

export enum BUTTON_ACTION {
  QUIT_WITHOUT_SAVING = 'QUIT_WITHOUT_SAVING',
  CANCEL = 'CANCEL',
}

interface IButtonDefault {
  text: string
  actionType?: BUTTON_ACTION.CANCEL | BUTTON_ACTION.QUIT_WITHOUT_SAVING
  action?: never
}
interface IButtonWithCustomAction {
  text: string
  action: () => void
  actionType?: never
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
  rightButton?: IButtonDefault | IButtonWithCustomAction
  leftButton?: IButtonDefault | IButtonWithCustomAction
}

const RouteLeavingGuard = ({
  children,
  extraClassNames = '',
  shouldBlockNavigation,
  when,
  dialogTitle,
  tracking,
  rightButton = {
    text: 'Quitter',
  },
  leftButton = { text: 'Annuler' },
}: IRouteLeavingGuardProps): JSX.Element => {
  const [isModalVisible, setIsModalVisible] = useState(false)
  // @ts-ignore next FIX ME no any
  const [nextLocation, setNextLocation] = useState<any>('')
  const [isConfirmedNavigation, setIsConfirmedNavigation] = useState(false)
  const history = useHistory()

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

  const closeModal = useCallback(() => {
    setIsModalVisible(false)
  }, [])

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

  const rightButtonAction = () => {
    if (typeof rightButton.action === 'function') {
      return () => {
        rightButton.action && rightButton.action()
        handleConfirmNavigationClick()
      }
    } else if (rightButton.actionType === BUTTON_ACTION.CANCEL) {
      return closeModal
    }
    return handleConfirmNavigationClick
  }

  const leftButtonAction = () => {
    if (typeof leftButton.action === 'function') {
      return () => {
        leftButton.action && leftButton.action()
        handleConfirmNavigationClick()
      }
    } else if (leftButton.actionType === BUTTON_ACTION.QUIT_WITHOUT_SAVING) {
      return handleConfirmNavigationClick
    }
    return closeModal
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
          onConfirm={rightButtonAction()}
          title={dialogTitle}
          confirmText={rightButton.text}
          cancelText={leftButton.text}
          leftButtonAction={leftButtonAction()}
        >
          {children}
        </ConfirmDialog>
      )}
    </>
  )
}

export default RouteLeavingGuard
