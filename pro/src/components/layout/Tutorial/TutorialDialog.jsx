import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import DialogBox from 'new_components/DialogBox/DialogBox'
import { Tutorial, TUTO_DIALOG_LABEL_ID } from 'new_components/Tutorial'
import * as pcapi from 'repository/pcapi/pcapi'

import styles from './TutorialDialog.module.scss'

const TutorialDialog = ({ currentUser, setUserHasSeenTuto }) => {
  const [areTutoDisplayed, setAreTutoDisplayed] = useState(
    currentUser && !currentUser.hasSeenProTutorials
  )

  const saveHasSeenProTutorials = useCallback(() => {
    pcapi
      .setHasSeenTutos()
      .then(() => {
        setUserHasSeenTuto(currentUser)
      })
      .finally(() => setAreTutoDisplayed(false))
  }, [currentUser, setUserHasSeenTuto])

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
