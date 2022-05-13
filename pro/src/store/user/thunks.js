import * as pcapi from 'repository/pcapi/pcapi'

import { setIsInitialized } from './actions'
import { setUsers } from 'store/reducers/data'

export const loadUser = () => dispatch =>
  pcapi
    .getUserInformations()
    .then(user => {
      // TODO: state.data.users have to be moved into state.user.currentUser
      dispatch(setUsers([user ? user : null]))
    })
    .catch(() => setUsers([null]))
    .finally(() => {
      dispatch(setIsInitialized(true))
    })

export const signin = (emailValue, passwordValue, success, fail) => dispatch =>
  pcapi
    .signin({ identifier: emailValue, password: passwordValue })
    .then(user => {
      // TODO: state.data.users have to be moved into state.user.currentUser
      dispatch(setUsers([user ? user : null]))
      success()
    })
    .catch(payload => {
      setUsers([null])
      fail(payload)
    })
