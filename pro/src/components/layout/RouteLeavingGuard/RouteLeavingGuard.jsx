/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useCallback, useState, useRef } from 'react'
import { Redirect } from 'react-router'
import { Prompt } from 'react-router-dom'

import DialogBox from 'new_components/DialogBox/DialogBox'

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

  const confirmButtonRef = useRef()

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

  // eslint-disable-next-line react/display-name, react/no-multi-comp
  const ConfirmButton = React.forwardRef((props, ref) => (
    <button
      className="primary-button"
      // eslint-disable-next-line react/prop-types
      onClick={props.onClick}
      ref={ref}
      type="button"
    >
      Quitter
    </button>
  ))

  return isConfirmedNavigation && lastLocation ? (
    <Redirect push to={lastLocation} />
  ) : (
    <>
      <Prompt message={handleBlockedNavigation} when={when} />
      {isModalVisible && (
        <DialogBox
          extraClassNames={extraClassNames}
          hasCloseButton={false}
          initialFocusRef={confirmButtonRef}
          labelledBy={labelledBy}
          onDismiss={closeModal}
        >
          {children}
          <div className="action-buttons">
            <button
              className="secondary-button"
              onClick={closeModal}
              type="button"
            >
              Annuler
            </button>
            <ConfirmButton
              onClick={handleConfirmNavigationClick}
              ref={confirmButtonRef}
            />
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
