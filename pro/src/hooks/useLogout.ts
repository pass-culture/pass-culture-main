import { useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { resetIsInitialized } from 'store/user/actions'

export const useLogout = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch()

  const logout = useCallback(async () => {
    await api.signout()
    dispatch(resetIsInitialized())

    navigate(`/connexion`)
  }, [navigate, dispatch])

  return logout
}
