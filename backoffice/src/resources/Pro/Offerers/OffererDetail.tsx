import {
  Button,
  Card,
  CircularProgress,
  Grid,
  Stack,
  Typography,
} from '@mui/material'
import React from 'react'
import {
  useAuthenticated,
  useGetOne,
  usePermissions,
  useRedirect,
} from 'react-admin'
import { useParams } from 'react-router-dom'

import { searchPermission } from '../../../helpers/functions'
import { Colors } from '../../../layout/Colors'
import { eventMonitoring } from '../../../libs/monitoring/sentry'
import { StatusBadge } from '../../PublicUsers/Components/StatusBadge'
import { PermissionsEnum } from '../../PublicUsers/types'
import { ProTypeBadge } from '../Components/ProTypeBadge'
import { ProTypeEnum } from '../types'

const cardStyle = {
  maxWidth: '99vw',
  width: '100%',
  marginTop: '20px',
  padding: 30,
}

export const OffererDetail = () => {
  useAuthenticated()
  const { id } = useParams()
  const { permissions } = usePermissions()
  const formattedPermissions: PermissionsEnum[] = permissions
  const canReadProEntity = !!searchPermission(
    formattedPermissions,
    PermissionsEnum.readProEntity
  )
  const redirect = useRedirect()

  const { data: offererInfo, isLoading } = useGetOne(
    'offerer',
    { id: id },
    // redirect to the list if the book is not found
    { onError: () => redirect('/pro/search') }
  )
  if (isLoading) {
    return <CircularProgress size={18} thickness={2} />
  } else if (!offererInfo) {
    eventMonitoring.captureException(new Error('NO_USER_BASE_INFO_LOADED'), {
      extra: { id },
    })
    return <CircularProgress size={18} thickness={2} />
  }
  const offererStats = offererInfo.stats
  const totalActiveOffers =
    offererStats.active.individual + offererStats.active.collective
  const totalInactiveOffers =
    offererStats.inactive.individual + offererStats.inactive.collective
  const offererRevenue = offererInfo.revenue

  const activeBadge = <StatusBadge active={offererInfo.isActive} />
  const protypeBadge = (
    <ProTypeBadge type={ProTypeEnum.offerer} resource={offererInfo} />
  )

  return (
    <Grid
      container
      spacing={0}
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{ maxWidth: '99vw', width: '100%' }}
    >
      {canReadProEntity && (
        <>
          <Grid container spacing={1} sx={{ mt: 3, ml: 1 }}>
            <Grid item xs={10}>
              <Typography variant={'h5'} component={'div'} color={Colors.GREY}>
                Acteurs culturels
              </Typography>
            </Grid>
            <Grid item xs={2}>
              <Button onClick={() => history.back()} variant={'text'}>
                &lt; Retour à la recherche
              </Button>
            </Grid>
          </Grid>
          <Card style={cardStyle}>
            <Grid container spacing={1}>
              <Grid item xs={10}>
                <Grid container spacing={1}>
                  <Grid item xs={12}>
                    <div>
                      <Typography variant="h5" gutterBottom component="div">
                        {offererInfo.name}
                        &nbsp; &nbsp; {offererInfo.isActive && activeBadge}{' '}
                        &nbsp; {offererInfo && protypeBadge}
                      </Typography>
                      <Typography
                        variant="body1"
                        gutterBottom
                        component="div"
                        color={Colors.GREY}
                      >
                        Offerer ID : {offererInfo.id}
                      </Typography>
                      <Typography
                        variant="body1"
                        gutterBottom
                        component="div"
                        color={Colors.GREY}
                      >
                        SIREN : {offererInfo.siren}
                      </Typography>
                    </div>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body1" gutterBottom component="div">
                      <strong>Eligible EAC : </strong>
                      {offererInfo.isCollectiveEligible == true ? 'OUI' : 'NON'}
                    </Typography>

                    <Typography variant="body1" gutterBottom component="div">
                      <strong>Région CT : </strong>
                      {offererInfo.region}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    {/*  TODO: PRESENCE CB */}
                    <Typography variant="body1" gutterBottom component="div">
                      <strong>Présence CB dans les lieux: </strong>
                      {offererInfo.bankInformationStatus.ok} OK /{' '}
                      {offererInfo.bankInformationStatus.ko} KO
                    </Typography>
                    {/*  TODO: DMS STATUS */}
                  </Grid>
                </Grid>
              </Grid>
              <Grid item xs={2}>
                <div>
                  <Stack spacing={2}>
                    <Button
                      variant={'contained'}
                      disabled
                      style={{ visibility: 'hidden' }}
                    >
                      Suspendre un rattachement
                    </Button>
                    <Button
                      variant={'contained'}
                      disabled
                      style={{ visibility: 'hidden' }}
                    >
                      Suspendre le compte
                    </Button>
                  </Stack>
                </div>
                <div>
                  <Stack spacing={2}>
                    <Button
                      disabled={offererInfo.dmsUrl == null}
                      variant={'text'}
                    >
                      Accéder au dossier DMS
                    </Button>
                  </Stack>
                </div>
              </Grid>
            </Grid>
          </Card>
          <Grid container spacing={1}>
            <Grid item xs={4}>
              {/* CA GENERE */}
              <Card style={{ ...cardStyle, height: '9rem' }}>
                <Typography variant={'h4'} component={'div'}>
                  {offererRevenue}&euro;
                </Typography>
                <Typography variant={'caption'}> de CA </Typography>
              </Card>
            </Grid>
            <Grid item xs={4}>
              {/* STATS OFFERS */}
              <Card style={{ ...cardStyle, height: '9rem' }}>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Stack direction={'column'}>
                      <Typography variant={'h4'}>
                        {totalActiveOffers}
                      </Typography>
                      <Typography variant={'body1'} color={Colors.GREY}>
                        offres actives ({offererStats.active.individual} IND /{' '}
                        {offererStats.active.collective} EAC)
                      </Typography>
                    </Stack>
                  </Grid>
                  <Grid item xs={6}>
                    <Stack direction={'column'}>
                      <Typography variant={'h4'}>
                        {totalInactiveOffers}
                      </Typography>
                      <Typography variant={'body1'} color={Colors.GREY}>
                        offres inactives
                      </Typography>
                    </Stack>
                  </Grid>
                </Grid>
              </Card>
            </Grid>
            <Grid item xs={4}>
              {/* REIMBURSEMENTS */}
              <Card
                style={{
                  ...cardStyle,
                  height: '9rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant={'h5'}>
                  {/*Dossier*/}
                  {/*<strong*/}
                  {/*  style={{ marginLeft: '0.5rem', marginRight: '0.5rem' }}*/}
                  {/*></strong>*/}
                  {/*<span style={{ marginRight: '0.35rem' }}>importé le :</span>*/}
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
      {!canReadProEntity && (
        <>
          <Typography variant={'h5'} color={Colors.GREY} sx={{ mb: 3, mt: 3 }}>
            Vous n'avez pas accès à cette page !
          </Typography>
          <div>
            <Button variant={'outlined'} onClick={() => history.back()}>
              Retour à la page précédente
            </Button>
          </div>
        </>
      )}
    </Grid>
  )
}
