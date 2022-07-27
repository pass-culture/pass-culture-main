import React, { ReactNode, useCallback, useState } from 'react'
import { Redirect, useHistory, Prompt } from 'react-router-dom'

import DialogBox from 'new_components/DialogBox/DialogBox'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './RouteLeavingGuard.module.scss'

export interface IShouldBlockNavigationReturnValue {
  redirectPath?: string | null
  shouldBlock: boolean
}
export interface IRouteLeavingGuardProps {
  children: ReactNode | ReactNode[]
  extraClassNames?: string
  labelledBy: string
  shouldBlockNavigation: (
    location: Location
  ) => IShouldBlockNavigationReturnValue
  when: boolean
}

const RouteLeavingGuard = ({
  children,
  extraClassNames = '',
  labelledBy,
  shouldBlockNavigation,
  when,
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
        <DialogBox
          extraClassNames={extraClassNames}
          hasCloseButton={false}
          labelledBy={labelledBy}
          onDismiss={closeModal}
        >
          {children}
          <div className={styles['action-buttons']}>
            <Button
              className={styles['action-button']}
              onClick={closeModal}
              type="button"
              variant={ButtonVariant.SECONDARY}
            >
              Annuler
            </Button>
            <Button
              className={styles['action-button']}
              onClick={handleConfirmNavigationClick}
              type="button"
            >
              Quitter
            </Button>
          </div>
        </DialogBox>
      )}
    </>
  )
}

export default RouteLeavingGuard
