import React, { ReactNode, useCallback, useState } from 'react'
import { Redirect, Prompt } from 'react-router-dom'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { useNavigate } from 'hooks'

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

const isIButtonWithCustomAction = (
  buttonData: IButtonDefault | IButtonWithCustomAction
): buttonData is IButtonWithCustomAction => {
  return buttonData.action !== undefined
}
interface IButtonWithCustomAction {
  text: string
  action?: () => void | Promise<void>
  actionType?: never
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

  const closeModal = useCallback(() => {
    setIsModalVisible(false)
  }, [])

  const handleConfirmNavigationClick = useCallback(() => {
    setIsModalVisible(false)
    setIsConfirmedNavigation(true)
  }, [])

  const trackWhenQuit = useCallback(() => {
    tracking &&
      tracking(
        Object.keys(nextLocation).includes('pathname')
          ? nextLocation.pathname
          : nextLocation
      )
  }, [isConfirmedNavigation, nextLocation])

  const rightButtonAction = () => {
    if (isIButtonWithCustomAction(rightButton)) {
      return async () => {
        rightButton.action && (await rightButton.action())
        handleConfirmNavigationClick()
        trackWhenQuit()
      }
    } else if (rightButton.actionType === BUTTON_ACTION.CANCEL) {
      return closeModal
    }
    return () => {
      handleConfirmNavigationClick()
      trackWhenQuit()
    }
  }

  const leftButtonAction = () => {
    if (isIButtonWithCustomAction(leftButton)) {
      return async () => {
        leftButton.action && (await leftButton.action())
        handleConfirmNavigationClick()
        trackWhenQuit()
      }
    } else if (leftButton.actionType === BUTTON_ACTION.QUIT_WITHOUT_SAVING) {
      return () => {
        handleConfirmNavigationClick()
        trackWhenQuit()
      }
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
