import {
  alpha,
  Box,
  Button,
  Card,
  CircularProgress,
  Grid,
  Paper,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Typography,
} from '@mui/material'
import { format } from 'date-fns'
import React, { useCallback, useState } from 'react'
import {
  useAuthenticated,
  useGetOne,
  useNotify,
  usePermissions,
  useRedirect,
} from 'react-admin'
import { useParams } from 'react-router-dom'

import { searchPermission, uuid } from '../../../helpers/functions'
import { Colors } from '../../../layout/Colors'
import { eventMonitoring } from '../../../libs/monitoring/sentry'
import { HistoryItem, OffererAttachedUser } from '../../../TypesFromApi'
import { StatusBadge } from '../../PublicUsers/Components/StatusBadge'
import { PermissionsEnum } from '../../PublicUsers/types'
import { BankAccountStatusBadge } from '../Components/BankAccountStatusBadge'
import { CommentOfferer } from '../Components/CommentOfferer'
import { OffererUserssToValidateContextTableMenu } from '../Components/OffererUsersToValidateContextTableMenu'
import { ProTypeBadge } from '../Components/ProTypeBadge'
import { ValidationStatusBadge } from '../Components/VallidationStatusBadge'
import { ProTypeEnum } from '../types'

const cardStyle = {
  maxWidth: '99vw',
  width: '100%',
  marginTop: '20px',
  padding: 30,
}

const tabStyle = { bgcolor: alpha(Colors.GREY, 0.1) }

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      style={{ maxWidth: '99vw', width: '100%' }}
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  )
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  }
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
  const notify = useNotify()
  const redirect = useRedirect()
  const [tabValue, setTabValue] = useState(0)
  const handleChange = useCallback(
    (event: React.SyntheticEvent, newValue: number) => {
      setTabValue(newValue)
    },
    [setTabValue]
  )
  const { data: offererInfo, isLoading } = useGetOne(
    'offerer',
    { id: id },
    // redirect to the list if the book is not found
    {
      onError() {
        notify(`Une erreur est survenue`, {
          type: 'error',
        })
        redirect('/pro/search')
      },
    }
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
  const offererUsers: OffererAttachedUser[] = offererInfo.users
  const offererHistory: HistoryItem[] = offererInfo.history.sort(
    (a: HistoryItem, b: HistoryItem) => (a.date < b.date ? 1 : -1)
  )

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
                      <BankAccountStatusBadge
                        OK={offererInfo.bankInformationStatus.ok}
                        KO={offererInfo.bankInformationStatus.ko}
                      />
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
          <Grid container spacing={2} sx={{ mt: 3 }}>
            <Box
              sx={{
                borderBottom: 1,
                borderColor: 'divider',
                width: '100%',
              }}
            >
              <Tabs
                value={tabValue}
                onChange={handleChange}
                aria-label="basic tabs example"
                variant="fullWidth"
              >
                <Tab
                  label="Historique du compte"
                  {...a11yProps(0)}
                  sx={tabStyle}
                />
                <Tab
                  label="Compte(s) Pro(s) Rattaché(s)"
                  {...a11yProps(1)}
                  sx={tabStyle}
                />
                <Tab label="" {...a11yProps(2)} disabled />
              </Tabs>
              <TabPanel value={tabValue} index={0}>
                <CommentOfferer offererId={offererInfo.id} />
                <TableContainer component={Paper} elevation={3}>
                  <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <TableHead>
                      <TableRow>
                        <TableCell>&nbsp;</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Date/Heure</TableCell>
                        <TableCell align="left">Auteur</TableCell>
                        <TableCell align="left">Commentaire</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {offererHistory.map(item => (
                        <TableRow
                          key={uuid()}
                          sx={{
                            '&:last-child td, &:last-child th': { border: 0 },
                          }}
                        >
                          <TableCell component="th" scope="row"></TableCell>
                          <TableCell>{item.type}</TableCell>
                          <TableCell>
                            {format(item.date, 'dd/MM/yyyy à HH:mm:ss')}
                          </TableCell>
                          <TableCell align="left">{item.authorName}</TableCell>
                          <TableCell align="left">
                            <p>{`${item.accountName} - ${item.accountId}`}</p>
                            <span>{`Commentaire :
                              ${item.comment}`}</span>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </TabPanel>
              <TabPanel value={tabValue} index={1}>
                <TableContainer component={Paper} elevation={3}>
                  <Table sx={{ minWidth: 650 }} aria-label="simple table">
                    <TableHead>
                      <TableRow>
                        <TableCell></TableCell>
                        <TableCell>ID</TableCell>
                        <TableCell>Statut</TableCell>
                        <TableCell>Nom</TableCell>
                        <TableCell>Prénom</TableCell>
                        <TableCell align="left">Email</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {offererUsers.map(user => (
                        <TableRow
                          key={user.id}
                          sx={{
                            '&:last-child td, &:last-child th': { border: 0 },
                          }}
                        >
                          <TableCell>
                            <OffererUserssToValidateContextTableMenu
                              id={user.userOffererId}
                            />
                          </TableCell>
                          <TableCell>{user.id}</TableCell>
                          <TableCell>
                            <ValidationStatusBadge
                              status={user.validationStatus}
                            />
                          </TableCell>
                          <TableCell component="th" scope="row">
                            {user.lastName}
                          </TableCell>
                          <TableCell>{user.firstName}</TableCell>
                          <TableCell align="left">{user.email}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </TabPanel>
              <TabPanel value={tabValue} index={2}>
                Bientôt disponible
              </TabPanel>
            </Box>
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
