import React, { useState } from 'react'
import { useLogin as userLogin } from 'react-admin'
import { Button, CardActions, CircularProgress } from '@mui/material'
import {
  GoogleLoginResponse,
  GoogleLoginResponseOffline,
  useGoogleLogin,
} from 'react-google-login'

export const LoginForm = () => {
  const [loading, setLoading] = useState(false)
  const login = userLogin()

  const onLoginSucess = (
    response: GoogleLoginResponse | GoogleLoginResponseOffline
  ) => {
    setLoading(false)
    if ('getAuthResponse' in response) {
      login({ token: response.getAuthResponse() })
    }
  }
  const client_id = process.env.REACT_APP_OIDC_CLIENT_ID

  const { signIn } = useGoogleLogin({
    clientId: client_id ? client_id : 'test',
    onSuccess: onLoginSucess,
  })

  const handleLogin = async () => {
    setLoading(true)
    signIn()
  }

  return (
    <div>
      <CardActions>
        <Button
          variant="contained"
          type="submit"
          color="primary"
          onClick={handleLogin}
          disabled={loading}
        >
          {loading && <CircularProgress size={18} thickness={2} />}
          Login With Google
        </Button>
      </CardActions>
    </div>
  )
}
