import { Button, Grid } from '@mui/material'
import React from 'react'
import { useAuthenticated } from 'react-admin'

export const ProUserDetail = () => {
  useAuthenticated()

  return (
    <Grid
      container
      spacing={0}
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{ maxWidth: '99vw', width: '100%', height: '100%' }}
    >
      La page de détails d'un compte pro sera bientôt disponible.
      <br />
      <br />
      <Button onClick={() => history.back()} variant={'contained'}>
        {' '}
        &lt; Retour
      </Button>
    </Grid>
  )
}
