import React, { useCallback, useState } from 'react'
import { useDispatch } from 'react-redux'

import { api } from 'apiClient/api'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import { DialogBox } from 'new_components/DialogBox'
import { TUTO_DIALOG_LABEL_ID, Tutorial } from 'new_components/Tutorial'
import { setCurrentUser } from 'store/user/actions'

import styles from './TutorialDialog.module.scss'

const TutorialDialog = (): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()
  const [areTutoDisplayed, setAreTutoDisplayed] = useState(
    currentUser && !currentUser.hasSeenProTutorials
  )
  const { logEvent } = useAnalytics()

  const saveHasSeenProTutorials = useCallback(() => {
    logEvent?.(Events.FIRST_LOGIN)
    api
      .patchUserTutoSeen()
      .then(() => {
        dispatch(setCurrentUser({ ...currentUser, hasSeenProTutorials: true }))
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
  ) : (
    <></>
  )
}

export default TutorialDialog
