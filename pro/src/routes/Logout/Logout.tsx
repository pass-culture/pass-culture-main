import { useDispatch } from 'react-redux'
import { useHistory } from 'react-router'

import { signout } from 'repository/pcapi/pcapi'
import { resetIsInitialized } from 'store/user/actions'

const Logout = (): null => {
  const history = useHistory()
  const dispatch = useDispatch()
  signout().then(() => {
    dispatch(resetIsInitialized())
    history.push(`/connexion`)
  })

  return null
}

export default Logout
