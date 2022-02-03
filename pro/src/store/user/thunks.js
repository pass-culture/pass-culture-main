import * as pcapi from 'repository/pcapi/pcapi'
import { setUsers } from 'store/reducers/data'

import { setIsInitialized } from './actions'

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
