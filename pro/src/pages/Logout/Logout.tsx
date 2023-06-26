import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { resetIsInitialized } from 'store/user/actions'

const Logout = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch()

  api.signout().then(() => {
    dispatch(resetIsInitialized())

    if (window.Beamer !== undefined) {
      window.Beamer.destroy()
    }

    navigate(`/connexion`)
  })

  return null
}

export default Logout
