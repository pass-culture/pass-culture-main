import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { resetIsInitialized } from 'store/user/actions'

const Logout = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch()

  useEffect(() => {
    const logout = async () => {
      await api.signout()
      dispatch(resetIsInitialized())

      navigate(`/connexion`)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    logout()
  }, [])

  return null
}

export default Logout
