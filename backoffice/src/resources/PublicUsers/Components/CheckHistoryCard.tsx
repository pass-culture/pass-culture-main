import { Card } from '@material-ui/core'
import {
  FormControlLabel,
  Grid,
  Stack,
  Switch,
  Typography,
} from '@mui/material'
import moment from 'moment'
import React, { useState } from 'react'

import { snakeCaseToTitleCase } from '../../../tools/textTools'
import { CheckHistory } from '../types'

import { StatusAvatar } from './StatusAvatar'

type Props = {
  idCheckHistory: CheckHistory
}

export const CheckHistoryCard = ({ idCheckHistory }: Props) => {
  const cardStyle = {
    width: '100%',
    marginTop: '20px',
    padding: 30,
  }
  const gridStyle = { width: '100%', height: '100%', overflow: 'auto' }

  const [checked, setChecked] = useState(false)

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setChecked(event.target.checked)
  }

  return (
    <Card style={cardStyle}>
      <Grid container spacing={1}>
        <Typography variant={'h5'}>
          {snakeCaseToTitleCase(idCheckHistory.type as string)}
        </Typography>
        <Grid container spacing={1} sx={{ mt: 4 }}>
          <Stack spacing={2} direction={'row'} style={{ width: '100%' }}>
            <Grid item xs={6}>
              <p>Date de création</p>
            </Grid>
            <Grid item xs={6}>
              <p>
                {moment(idCheckHistory.dateCreated).format(
                  'D/MM/YYYY à HH:mm:s'
                )}
              </p>
            </Grid>
          </Stack>
          <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
            <Grid item xs={6}>
              <p>ID Technique</p>
            </Grid>
            <Grid item xs={6}>
              <p>{idCheckHistory.thirdPartyId}</p>
            </Grid>
          </Stack>
          <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
            <Grid item xs={6}>
              <p>Statut</p>
            </Grid>
            <Grid item xs={6}>
              <p>
                <StatusAvatar subscriptionItem={idCheckHistory} />
              </p>
            </Grid>
          </Stack>
          <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
            <Grid item xs={6}>
              <p>Explication</p>
            </Grid>
            <Grid item xs={6}>
              <p>{idCheckHistory.reason && idCheckHistory.reason}</p>
            </Grid>
          </Stack>
          <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
            <Grid item xs={6}>
              <p>Code d'erreurs</p>
            </Grid>
            <Grid item xs={6}>
              <p>{idCheckHistory.reasonCodes && idCheckHistory.reasonCodes}</p>
            </Grid>
          </Stack>

          <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
            <Grid item xs={6}>
              <p>Détails techniques</p>
              <FormControlLabel
                control={
                  <Switch
                    checked={checked}
                    onChange={handleChange}
                    inputProps={{ 'aria-label': 'controlled' }}
                    name={idCheckHistory.type}
                  />
                }
                label="Afficher les détails techniques"
              />
            </Grid>
            <Grid item xs={6}>
              <Grid container spacing={0}>
                <Grid item style={gridStyle}>
                  <code style={{ visibility: !checked ? 'hidden' : 'visible' }}>
                    {idCheckHistory.technicalDetails &&
                      JSON.stringify(
                        idCheckHistory.technicalDetails,
                        undefined,
                        4
                      )}
                  </code>
                </Grid>
              </Grid>
            </Grid>
          </Stack>
        </Grid>
      </Grid>
    </Card>
  )
}
