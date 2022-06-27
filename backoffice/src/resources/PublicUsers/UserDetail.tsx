import { Card } from '@material-ui/core'
import {
  Box,
  Button,
  CircularProgress,
  Grid,
  LinearProgress,
  Link,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Stack,
  Tab,
  Tabs,
  Typography,
} from '@mui/material'
import moment from 'moment'
import React, { useState } from 'react'
import {
  Identifier,
  useAuthenticated,
  useGetOne,
  useRedirect,
} from 'react-admin'
import { useParams } from 'react-router-dom'

import { Colors } from '../../layout/Colors'
import { eventMonitoring } from '../../libs/monitoring/sentry'

import { BeneficiaryBadge } from './BeneficiaryBadge'
import { CheckHistoryCard } from './CheckHistoryCard'
import { ManualReviewModal } from './ManualReviewModal'
import { StatusAvatar } from './StatusAvatar'
import { StatusBadge } from './StatusBadge'
import {
  CheckHistory,
  SubscriptionItem,
  SubscriptionItemStatus,
  SubscriptionItemType,
  UserBaseInfo,
} from './types'
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
  const [value, setValue] = useState(1)

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue)
  }

  const { data: userBaseInfo, isLoading } = useGetOne<UserBaseInfo>(
    'public_accounts',
    { id: id as Identifier },
    // redirect to the list if the book is not found
    { onError: () => redirect('/public_users/search') }
  )

  if (isLoading) {
    return <CircularProgress size={18} thickness={2} />
  } else if (!userBaseInfo) {
    eventMonitoring.captureException(new Error('NO_USER_BASE_INFO_LOADED'), {
      extra: { id },
    })
    return <CircularProgress size={18} thickness={2} />
  }

  const { remainingCredit, initialCredit } = userBaseInfo.userCredit
  const { AGE18, UNDERAGE } = userBaseInfo.userHistory.subscriptions

  const activeBadge = <StatusBadge active={userBaseInfo.isActive} />

  const beneficiaryBadge = <BeneficiaryBadge role={userBaseInfo.roles[0]} />

  const creditProgression = (remainingCredit / initialCredit) * 100

  const digitalCreditProgression = (remainingCredit / initialCredit) * 100

  let subscriptionItems: SubscriptionItem[] = []
  let idsCheckHistory: CheckHistory[] = []

  if (AGE18?.idCheckHistory?.length > 0) {
    idsCheckHistory = AGE18.idCheckHistory
    subscriptionItems = AGE18.subscriptionItems
  } else if (UNDERAGE?.idCheckHistory?.length > 0) {
    idsCheckHistory = UNDERAGE.idCheckHistory
    subscriptionItems = UNDERAGE.subscriptionItems
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
                    {userBaseInfo.isActive && activeBadge} &nbsp;{' '}
                    {userBaseInfo.roles[0] && beneficiaryBadge}
                  </Typography>
                  <Typography
                    variant="body1"
                    gutterBottom
                    component="div"
                    color={Colors.GREY}
                  >
                    User ID : {userBaseInfo.id}
                  </Typography>
                </div>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body1" gutterBottom component="div">
                  <strong>E-mail : </strong>
                  {userBaseInfo.email}
                </Typography>
                <Typography variant="body1" gutterBottom component="div">
                  <strong>Tél : </strong>
                  {userBaseInfo.phoneNumber}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body1" gutterBottom component="div">
                  Crédité le :{' '}
                  {userBaseInfo.userCredit &&
                    moment(userBaseInfo.userCredit.dateCreated).format(
                      'D/MM/YYYY'
                    )}
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
          <Card style={{ ...cardStyle, height: '9rem' }}>
            <Typography variant={'h5'}>
              {userBaseInfo.userCredit.remainingCredit}&euro;
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
                {userBaseInfo.userCredit.initialCredit}&euro;
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
          <Card style={{ ...cardStyle, height: '9rem' }}>
            <Typography variant={'h5'}>
              {userBaseInfo.userCredit.remainingDigitalCredit}&euro;
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
                {userBaseInfo.userCredit.initialCredit}&euro;
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
              Dossier{' '}
              <strong>
                {idsCheckHistory[0] && idsCheckHistory[0]['type']}
              </strong>{' '}
              importé le :{' '}
              {idsCheckHistory[0] &&
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
            <Tab label="" {...a11yProps(0)} disabled />
            <Tab label="Informations Personnelles" {...a11yProps(1)} />
            <Tab label="" {...a11yProps(2)} disabled />
          </Tabs>
        </Box>
        <TabPanel value={value} index={0}>
          Bientôt disponible
        </TabPanel>
        <TabPanel value={value} index={1}>
          <Stack spacing={3}>
            <Card style={cardStyle}>
              <Typography variant={'body1'} sx={{ color: Colors.GREY, mb: 4 }}>
                Accès
              </Typography>
              <Grid container spacing={5}>
                <Grid item xs={4}>
                  <Link
                    role={'link'}
                    href={'#details-user'}
                    color={Colors.GREY}
                    variant="body2"
                  >
                    DÉTAILS UTILISATEUR
                  </Link>
                </Grid>
                <Grid item xs={4}>
                  <Link
                    role={'link'}
                    href={'#parcours-register'}
                    color={Colors.GREY}
                    variant="body2"
                  >
                    PARCOURS D'INSCRIPTION
                  </Link>
                </Grid>
                {idsCheckHistory.map(idCheckHistory => (
                  <Grid item xs={4}>
                    <Link
                      role={'link'}
                      href={`#${idCheckHistory.thirdPartyId}`}
                      color={Colors.GREY}
                      variant="body2"
                    >
                      {idCheckHistory.type.toUpperCase()}
                    </Link>
                  </Grid>
                ))}
              </Grid>
            </Card>
            <div id="details-user">
              <UserDetailsCard
                user={userBaseInfo}
                firstIdCheckHistory={idsCheckHistory[0]}
              />
            </div>
            <div id="parcours-register">
              <Card style={cardStyle}>
                <Typography variant={'h5'}>
                  Parcours d'inscription{' '}
                  <span style={{ marginLeft: '3rem' }}>{beneficiaryBadge}</span>
                </Typography>
                {subscriptionItems.length > 0 && (
                  <>
                    <Grid container spacing={5} sx={{ mt: 4 }}>
                      <Grid item xs={6}>
                        <List sx={{ width: '100%' }}>
                          <ListItem>
                            <ListItemText> Validation email</ListItemText>
                            <ListItemAvatar>
                              {' '}
                              <StatusAvatar
                                subscriptionItem={subscriptionItems.find(
                                  subscriptionItem =>
                                    subscriptionItem.type ===
                                    SubscriptionItemType.EMAIL_VALIDATION
                                )}
                              />
                            </ListItemAvatar>
                          </ListItem>
                          <ListItem>
                            <ListItemText>Validation Téléphone</ListItemText>
                            <ListItemAvatar>
                              {' '}
                              <StatusAvatar
                                subscriptionItem={subscriptionItems.find(
                                  (item: {
                                    type: string
                                    status: SubscriptionItemStatus
                                  }) =>
                                    item.type ===
                                    SubscriptionItemType.PHONE_VALIDATION
                                )}
                              />
                            </ListItemAvatar>
                          </ListItem>
                          <ListItem>
                            <ListItemText>Profil Utilisateur</ListItemText>
                            <ListItemAvatar>
                              {' '}
                              <StatusAvatar
                                subscriptionItem={subscriptionItems.find(
                                  item =>
                                    item.type ===
                                    SubscriptionItemType.PROFILE_COMPLETION
                                )}
                              />
                            </ListItemAvatar>
                          </ListItem>
                        </List>
                      </Grid>

                      <Grid item xs={6}>
                        <List sx={{ width: '100%' }}>
                          <ListItem>
                            <ListItemText>Complétion Profil</ListItemText>
                            <ListItemAvatar>
                              {' '}
                              <StatusAvatar
                                subscriptionItem={subscriptionItems.find(
                                  (item: {
                                    type: string
                                    status: SubscriptionItemStatus
                                  }) =>
                                    item.type ===
                                    SubscriptionItemType.PROFILE_COMPLETION
                                )}
                              />
                            </ListItemAvatar>
                          </ListItem>
                          <ListItem>
                            <ListItemText>ID Check</ListItemText>
                            <ListItemAvatar>
                              {' '}
                              <StatusAvatar
                                subscriptionItem={subscriptionItems.find(
                                  item =>
                                    item.type ===
                                    SubscriptionItemType.IDENTITY_CHECK
                                )}
                              />
                            </ListItemAvatar>
                          </ListItem>
                          <ListItem>
                            <ListItemText>Honor Statement</ListItemText>
                            <ListItemAvatar>
                              {' '}
                              <StatusAvatar
                                subscriptionItem={subscriptionItems.find(
                                  (item: {
                                    type: string
                                    status: SubscriptionItemStatus
                                  }) =>
                                    item.type ===
                                    SubscriptionItemType.HONOR_STATEMENT
                                )}
                              />
                            </ListItemAvatar>
                          </ListItem>
                        </List>
                      </Grid>
                    </Grid>
                  </>
                )}
              </Card>
            </div>
            {idsCheckHistory.map(idCheckHistory => (
              <div id={idCheckHistory.thirdPartyId}>
                <CheckHistoryCard
                  key={idCheckHistory.thirdPartyId}
                  idCheckHistory={idCheckHistory}
                />
              </div>
            ))}
          </Stack>
        </TabPanel>
        <TabPanel value={value} index={2}>
          Bientôt disponible
        </TabPanel>
      </Grid>
    </Grid>
  )
}
