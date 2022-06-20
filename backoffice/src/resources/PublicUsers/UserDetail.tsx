import { Card } from '@material-ui/core'
import {
  Box,
  Button,
  CircularProgress,
  Grid,
  LinearProgress,
  Stack,
  Tab,
  Tabs,
  Typography,
} from '@mui/material'
import moment from 'moment'
import React from 'react'
import { useAuthenticated, useGetOne, useRedirect } from 'react-admin'
import { useParams } from 'react-router-dom'

import { BeneficiaryBadge } from './BeneficiaryBadge'
import { CheckHistoryCard } from './CheckHistoryCard'
import { ManualReviewModal } from './ManualReviewModal'
import { StatusAvatar } from './StatusAvatar'
import { StatusBadge } from './StatusBadge'
import { CheckHistory, SubscriptionItemStatus, UserBaseInfo } from './types'
import { UserDetailsCard } from './UserDetailsCard'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props

  return (
    <div
      style={{ width: '100%' }}
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

const cardStyle = {
  width: '100%',
  marginTop: '20px',
  padding: 30,
}

export const UserDetail = () => {
  useAuthenticated()
  const { id } = useParams() // this component is rendered in the /books/:id path
  const redirect = useRedirect()
  const [value, setValue] = React.useState(1)
  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue)
  }

  const { data, isLoading } = useGetOne(
    'public_accounts',
    { id },
    // redirect to the list if the book is not found
    { onError: () => redirect('/public_users/search') }
  )
  let subscriptionItems, idsCheckHistory, userData

  if (isLoading) {
    return <CircularProgress size={18} thickness={2} />
  }
  const userBaseInfo: UserBaseInfo = {
    address: data.address,
    city: data.city,
    dateOfBirth: data.dateOfBirth,
    email: data.email,
    firstName: data.firstName,
    id: data.id,
    lastName: data.lastName,
    phoneNumber: data.phoneNumber,
    postalCode: data.postalCode,
  }
  const activeBadge = <StatusBadge active={data.isActive} />
  const beneficiaryBadge = <BeneficiaryBadge role={data.roles[0]} />
  const creditProgression =
    (data.userCredit.remainingCredit / data.userCredit.initialCredit) * 100
  const digitalCreditProgression =
    (data.userCredit.remainingCredit / data.userCredit.initialCredit) * 100
  if (data.userHistory.subscriptions?.AGE18?.idCheckHistory?.length > 0) {
    userData = data.userHistory.subscriptions.AGE18
    if (userData) {
      idsCheckHistory = userData.idCheckHistory
      subscriptionItems = userData.subscriptionItems
    }
  } else if (
    data.userHistory.subscriptions?.UNDERAGE?.idCheckHistory?.length > 0
  ) {
    userData = data.userHistory.subscriptions.UNDERAGE
    if (userData) {
      idsCheckHistory = userData.idCheckHistory
      subscriptionItems = userData.subscriptionItems
    }
  }

  return (
    <Grid
      container
      spacing={0}
      direction="column"
      alignItems="center"
      justifyContent="center"
    >
      <Card style={cardStyle}>
        <Grid container spacing={1}>
          <Grid item xs={10}>
            <Grid container spacing={1}>
              <Grid item xs={12}>
                <div>
                  <Typography variant="h5" gutterBottom component="div">
                    {userBaseInfo.lastName}&nbsp;{userBaseInfo.firstName} &nbsp;{' '}
                    {data.isActive && activeBadge} &nbsp;{' '}
                    {data.roles[0] && beneficiaryBadge}
                  </Typography>
                  <Typography variant="body1" gutterBottom component="div">
                    User ID : {userBaseInfo.id}
                  </Typography>
                </div>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" gutterBottom component="div">
                  <strong>e-mail : </strong>
                  {userBaseInfo.email}
                </Typography>
                <Typography variant="body2" gutterBottom component="div">
                  <strong>tél : </strong>
                  {userBaseInfo.phoneNumber}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" gutterBottom component="div">
                  Crédité le :
                  {data.userCredit &&
                    moment(data.userCredit.dateCreated).format('D/MM/YYYY')}
                </Typography>
              </Grid>
            </Grid>
          </Grid>

          <Grid item xs={2}>
            <div>
              <Stack spacing={2}>
                <Button variant={'contained'} disabled>
                  Suspendre le compte
                </Button>

                <ManualReviewModal user={userBaseInfo} />
              </Stack>
            </div>
          </Grid>
        </Grid>
      </Card>
      <Grid container spacing={1}>
        <Grid item xs={4}>
          <Card style={cardStyle}>
            <Typography variant={'h5'}>
              {data.userCredit.remainingCredit}&euro;
            </Typography>
            <Stack
              direction={'row'}
              style={{
                width: '100%',
                justifyContent: 'space-between',
                marginTop: 12,
                marginBottom: 12,
              }}
              spacing={0}
            >
              <Typography variant={'body1'}>Crédit restant </Typography>
              <Typography variant={'body1'}>
                {data.userCredit.initialCredit}&euro;
              </Typography>
            </Stack>
            <LinearProgress
              style={{ width: '100%' }}
              color={'primary'}
              variant={'determinate'}
              value={creditProgression}
            />
          </Card>
        </Grid>
        <Grid item xs={4}>
          <Card style={cardStyle}>
            <Typography variant={'h5'}>
              {data.userCredit.remainingDigitalCredit}&euro;
            </Typography>
            <Stack
              direction={'row'}
              style={{
                width: '100%',
                justifyContent: 'space-between',
                marginTop: 12,
                marginBottom: 12,
              }}
              spacing={0}
            >
              <Typography variant={'body1'}>Crédit digital restant </Typography>
              <Typography variant={'body1'}>
                {data.userCredit.initialCredit}&euro;
              </Typography>
            </Stack>
            <LinearProgress
              style={{ width: '100%' }}
              color={'primary'}
              variant={'determinate'}
              value={digitalCreditProgression}
            />
          </Card>
        </Grid>
        <Grid item xs={4}>
          {/*Carte infos dossier d'importation */}
          <Card style={{ ...cardStyle, paddingBottom: 40 }}>
            <Typography variant={'h5'}>
              Dossier{' '}
              <strong>
                {idsCheckHistory &&
                  idsCheckHistory[0] &&
                  idsCheckHistory[0]['type']}
              </strong>{' '}
              importé le :
            </Typography>
            <Typography variant={'h4'}>
              {idsCheckHistory &&
                idsCheckHistory[0] &&
                moment(idsCheckHistory[0]['dateCreated']).format(
                  'D/MM/YYYY à HH:mm'
                )}
            </Typography>
          </Card>
        </Grid>
      </Grid>
      <Grid container spacing={2} sx={{ mt: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', width: '100%' }}>
          <Tabs
            value={value}
            onChange={handleChange}
            aria-label="basic tabs example"
            variant="fullWidth"
          >
            <Tab label="Historique du compte" {...a11yProps(0)} />
            <Tab label="Informations Personnelles" {...a11yProps(1)} />
            <Tab label="Suivi des réservations" {...a11yProps(2)} />
          </Tabs>
        </Box>
        <TabPanel value={value} index={0}>
          Bientôt disponible
        </TabPanel>
        <TabPanel value={value} index={1}>
          <Stack spacing={3}>
            <UserDetailsCard
              {...userBaseInfo}
              firstIdCheckHistory={
                idsCheckHistory && idsCheckHistory.length > 0
                  ? idsCheckHistory[0]
                  : null
              }
            />

            <Card style={cardStyle}>
              <Typography variant={'h5'}>
                Parcours d'inscription {beneficiaryBadge}
              </Typography>
              {subscriptionItems && (
                <>
                  <Grid container spacing={5} sx={{ mt: 4 }}>
                    <Grid item xs={6}>
                      <Stack
                        spacing={3}
                        direction={'row'}
                        style={{ width: '100%' }}
                      >
                        <Typography variant={'body1'}>
                          Validation email
                        </Typography>
                        {StatusAvatar(
                          subscriptionItems.find(
                            (item: {
                              type: string
                              status: SubscriptionItemStatus
                            }) => item.type === 'email-validation'
                          ).status
                        )}
                      </Stack>
                    </Grid>
                    <Grid item xs={6}>
                      <Stack
                        spacing={3}
                        direction={'row'}
                        style={{ width: '100%' }}
                      >
                        <Typography variant={'body1'}>
                          Complétion Profil
                        </Typography>
                        {StatusAvatar(
                          subscriptionItems.find(
                            (item: {
                              type: string
                              status: SubscriptionItemStatus
                            }) => item.type === 'profile-completion'
                          ).status
                        )}
                      </Stack>
                    </Grid>
                    <Grid item xs={6}>
                      <Stack
                        spacing={3}
                        direction={'row'}
                        style={{ width: '100%' }}
                      >
                        <Typography variant={'body1'}>
                          Validation Téléphone
                        </Typography>
                        {StatusAvatar(
                          subscriptionItems.find(
                            (item: {
                              type: string
                              status: SubscriptionItemStatus
                            }) => item.type === 'phone-validation'
                          ).status
                        )}
                      </Stack>
                    </Grid>
                    <Grid item xs={6}>
                      <Stack
                        spacing={3}
                        direction={'row'}
                        style={{ width: '100%' }}
                      >
                        <Typography variant={'body1'}>ID Check</Typography>
                        {StatusAvatar(
                          subscriptionItems.find(
                            (item: {
                              type: string
                              status: SubscriptionItemStatus
                            }) => item.type === 'identity-check'
                          ).status
                        )}
                      </Stack>
                    </Grid>
                    <Grid item xs={6}>
                      <Stack
                        spacing={3}
                        direction={'row'}
                        style={{ width: '100%' }}
                      >
                        <Typography variant={'body1'}>
                          Profil Utilisateur
                        </Typography>
                        {StatusAvatar(
                          subscriptionItems.find(
                            (item: {
                              type: string
                              status: SubscriptionItemStatus
                            }) => item.type === 'profile-completion'
                          ).status
                        )}
                      </Stack>
                    </Grid>
                    <Grid item xs={6}>
                      <Stack
                        spacing={3}
                        direction={'row'}
                        style={{ width: '100%' }}
                      >
                        <Typography variant={'body1'}>
                          Honor Statement
                        </Typography>
                        {StatusAvatar(
                          subscriptionItems.find(
                            (item: {
                              type: string
                              status: SubscriptionItemStatus
                            }) => item.type === 'honor-statement'
                          ).status
                        )}
                      </Stack>
                    </Grid>
                  </Grid>
                </>
              )}
            </Card>

            {idsCheckHistory &&
              idsCheckHistory.map((idCheckHistory: CheckHistory) => {
                return <CheckHistoryCard {...idCheckHistory} />
              })}
          </Stack>
        </TabPanel>
        <TabPanel value={value} index={2}>
          Bientôt disponible
        </TabPanel>
      </Grid>
    </Grid>
  )
}
