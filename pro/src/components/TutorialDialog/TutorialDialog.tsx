import React, { useCallback, useState } from 'react'
import { useDispatch } from 'react-redux'

import { api } from 'apiClient/api'
import useAnalytics from 'app/App/analytics/firebase'
import { DialogBox } from 'components/DialogBox/DialogBox'
import { TUTO_DIALOG_LABEL_ID } from 'components/Tutorial/constants'
import { Tutorial } from 'components/Tutorial/Tutorial'
import { Events } from 'core/FirebaseEvents/constants'
import { useCurrentUser } from 'hooks/useCurrentUser'
import { updateUser } from 'store/user/reducer'

import styles from './TutorialDialog.module.scss'

export const TutorialDialog = (): JSX.Element => {
  const { currentUser } = useCurrentUser()
  const dispatch = useDispatch()
  const [areTutoDisplayed, setAreTutoDisplayed] = useState(
    !currentUser.hasSeenProTutorials
  )
  const { logEvent } = useAnalytics()

  const saveHasSeenProTutorials = useCallback(() => {
    logEvent(Events.FIRST_LOGIN)
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    api
      .patchUserTutoSeen()
      .then(() => {
        dispatch(updateUser({ ...currentUser, hasSeenProTutorials: true }))
      })
      .finally(() => setAreTutoDisplayed(false))
  }, [currentUser, logEvent, dispatch])

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
