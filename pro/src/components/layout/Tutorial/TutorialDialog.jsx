import * as pcapi from 'repository/pcapi/pcapi'

import React, { useCallback, useState } from 'react'
import { TUTO_DIALOG_LABEL_ID, Tutorial } from 'new_components/Tutorial'

import DialogBox from 'new_components/DialogBox/DialogBox'
import { Events } from 'core/FirebaseEvents/constants'
import PropTypes from 'prop-types'
import styles from './TutorialDialog.module.scss'
import { useSelector } from 'react-redux'

const TutorialDialog = ({ currentUser, setUserHasSeenTuto }) => {
  const [areTutoDisplayed, setAreTutoDisplayed] = useState(
    currentUser && !currentUser.hasSeenProTutorials
  )
  const logEvent = useSelector(state => state.app.logEvent)

  const saveHasSeenProTutorials = useCallback(() => {
    logEvent(Events.FIRST_LOGIN)
    pcapi
      .setHasSeenTutos()
      .then(() => {
        setUserHasSeenTuto(currentUser)
      })
      .finally(() => setAreTutoDisplayed(false))
  }, [currentUser, setUserHasSeenTuto, logEvent])

  return areTutoDisplayed ? (
    <DialogBox
      extraClassNames={styles['tutorial-box']}
      hasCloseButton
      labelledBy={TUTO_DIALOG_LABEL_ID}
      onDismiss={saveHasSeenProTutorials}
    >
      <Tutorial onFinish={saveHasSeenProTutorials} />
    </DialogBox>
  ) : null
}

TutorialDialog.defaultProps = {
  currentUser: null,
}

TutorialDialog.propTypes = {
  currentUser: PropTypes.shape(),
  setUserHasSeenTuto: PropTypes.func.isRequired,
}

export default TutorialDialog
