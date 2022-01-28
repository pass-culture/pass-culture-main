import React, { useCallback, useState, ReactNode } from 'react'
import { Redirect } from 'react-router'
import { Prompt } from 'react-router-dom'

import DialogBox from 'new_components/DialogBox/DialogBox'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './RouteLeavingGuard.module.scss'
export interface IRouteLeavingGuardProps {
  children: ReactNode | ReactNode[]
  extraClassNames?: string
  labelledBy: string
  shouldBlockNavigation: (location: Location) => boolean
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

  const closeModal = useCallback(() => {
    setIsModalVisible(false)
  }, [])

  const handleBlockedNavigation = useCallback(
    nextLocation => {
      if (!isConfirmedNavigation && shouldBlockNavigation(nextLocation)) {
        setIsModalVisible(true)
        setLastLocation(nextLocation)
        return false
      }
      return true
    },
    [isConfirmedNavigation, shouldBlockNavigation]
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
