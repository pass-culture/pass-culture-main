import { useDispatch } from 'react-redux'
import { useHistory } from 'react-router'

import { api } from 'apiClient/api'
import { resetIsInitialized } from 'store/user/actions'

const Logout = (): null => {
  const history = useHistory()
  const dispatch = useDispatch()
  api.signout().then(() => {
    dispatch(resetIsInitialized())
    history.push(`/connexion`)
  })

  return null
}

export default Logout
