import {
  Card,
  CardActions,
  CardContent,
  Divider,
  Stack,
  Typography,
} from '@mui/material'
import { CredentialResponse, GoogleLogin } from '@react-oauth/google'
import React from 'react'
import { useLogin as userLogin } from 'react-admin'

import { Colors } from '../../layout/Colors'
import { Logo } from '../../layout/Logo'
import { GovernmentIcon } from '../Icons/GovernmentIcon'

export const LoginForm = () => {
  const login = userLogin()

  const onLoginSucess = (response: CredentialResponse) => {
    if (response) {
      login({ token: response.credential })
    }
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
        <GoogleLogin
          onSuccess={onLoginSucess}
          theme={'outline'}
          size={'large'}
          shape={'square'}
          text={'signin_with'}
          context={'signin'}
        />
      </CardActions>
    </Card>
  )
}
