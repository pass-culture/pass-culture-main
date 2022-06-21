import {
  Button,
  Card,
  CardActions,
  CardContent,
  CircularProgress,
  createSvgIcon,
  Divider,
  Stack,
  Typography,
} from '@mui/material'
import React, { useState } from 'react'
import { useLogin as userLogin } from 'react-admin'
import {
  GoogleLoginResponse,
  GoogleLoginResponseOffline,
  useGoogleLogin,
} from 'react-google-login'
import { GovernmentIcon } from '../Icons/GovernmentIcon'
import { Logo } from '../../layout/Logo'
import { red } from '@mui/material/colors'
import { inspect } from 'util'
import { Colors } from '../../layout/Colors'

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
    <Card variant="outlined" sx={{ p: 6 }}>
      <CardContent>
        <Stack
          direction={'row'}
          sx={{ mb: 4 }}
          style={{
            width: '100%',
            justifyContent: 'space-between',
            display: 'flex',
          }}
        >
          <GovernmentIcon />
          <Logo fill={Colors.THIRD} />
        </Stack>
        <Divider />
        <Typography variant="h4" component="div" sx={{ mt: 4 }}>
          Connexion au backoffice
        </Typography>
      </CardContent>
      <CardActions sx={{ my: 5 }}>
        <Button
          variant="contained"
          type="submit"
          color="primary"
          onClick={handleLogin}
          disabled={loading}
        >
          {loading && <CircularProgress size={18} thickness={2} />}
          M'authentifier avec Google
        </Button>
      </CardActions>
    </Card>
  )
}
