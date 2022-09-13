import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import useAnalytics from 'components/hooks/useAnalytics'
import useCurrentUser from 'components/hooks/useCurrentUser'
import { Events } from 'core/FirebaseEvents/constants'
import DialogBox from 'new_components/DialogBox/DialogBox'
import { TUTO_DIALOG_LABEL_ID, Tutorial } from 'new_components/Tutorial'
import * as pcapi from 'repository/pcapi/pcapi'
import { setCurrentUser } from 'store/user/actions'

import styles from './TutorialDialog.module.scss'

const TutorialDialog = () => {
  const { currentUser } = useCurrentUser()
  const [areTutoDisplayed, setAreTutoDisplayed] = useState(
    currentUser && !currentUser.hasSeenProTutorials
  )
  const { logEvent } = useAnalytics()

  const saveHasSeenProTutorials = useCallback(() => {
    logEvent?.(Events.FIRST_LOGIN)
    pcapi
      .setHasSeenTutos()
      .then(() => {
        setCurrentUser({ ...currentUser, hasSeenProTutorials: true })
      })
      .finally(() => setAreTutoDisplayed(false))
  }, [currentUser, logEvent])

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
