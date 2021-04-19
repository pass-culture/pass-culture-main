import PropTypes from 'prop-types'
import React, { useCallback, useState, useRef } from 'react'
import { Redirect } from 'react-router'
import { Prompt } from 'react-router-dom'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'

const RouteLeavingGuard = ({
  children,
  extraClassNames,
  labelledBy,
  shouldBlockNavigation,
  when,
}) => {
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [lastLocation, setLastLocation] = useState('')
  const [isConfirmedNavigation, setIsConfirmedNavigation] = useState(false)

  const confirmQuitButton = useRef()

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
    <Redirect
      push
      to={lastLocation}
    />
  ) : (
    <>
      <Prompt
        message={handleBlockedNavigation}
        when={when}
      />
      {isModalVisible && (
        <DialogBox
          extraClassNames={extraClassNames}
          labelledBy={labelledBy}
          onDismiss={closeModal}
          ref={confirmQuitButton}
        >
          {children}
          <div className="action-buttons">
            <button
              className="secondary-button"
              onClick={closeModal}
              type="button"
            >
              {'Annuler'}
            </button>
            <button
              className="primary-button"
              onClick={handleConfirmNavigationClick}
              ref={confirmQuitButton}
              type="button"
            >
              {'Quitter'}
            </button>
          </div>
        </DialogBox>
      )}
    </>
  )
}

RouteLeavingGuard.defaultProps = {
  extraClassNames: '',
}

RouteLeavingGuard.propTypes = {
  children: PropTypes.node.isRequired,
  extraClassNames: PropTypes.string,
  labelledBy: PropTypes.string.isRequired,
  shouldBlockNavigation: PropTypes.func.isRequired,
  when: PropTypes.bool.isRequired,
}

export default RouteLeavingGuard
