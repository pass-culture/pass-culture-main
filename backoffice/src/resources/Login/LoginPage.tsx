import { Grid } from '@mui/material'
import React from 'react'

import { BackgroundLogin } from '../Icons/BackgroundLogin'
import { Colors } from '../../layout/Colors'
import { LoginForm } from './LoginForm'

export const LoginPage = () => {
  return (
    <Grid
      container
      spacing={2}
      style={{
        justifyContent: 'center',
        display: 'flex',
      }}
      sx={{ p: 5 }}
    >
      <Grid item xs={6}>
        <BackgroundLogin
          fill={`linear-gradient(to right, ${Colors.PRIMARY}, ${Colors.SECONDARY});`}
          style={{
            zIndex: '-1',
            position: 'absolute',
            top: '3vh',
            left: '25vw',
          }}
        />
        <Grid style={{ position: 'absolute', top: '12vh', left: '25vw' }}>
          <LoginForm />
        </Grid>
      </Grid>
    </Grid>
  )
}
