import {
  alpha,
  Box,
  Button,
  Card,
  CircularProgress,
  Grid,
  LinearProgress,
  Link,
  Stack,
  Tab,
  Tabs,
  Typography,
} from '@mui/material'
import { captureException } from '@sentry/react'
import { format, parseISO } from 'date-fns'
import React, { useState } from 'react'
import {
  Identifier,
  useAuthenticated,
  useGetOne,
  useNotify,
  usePermissions,
  useRedirect,
} from 'react-admin'
import { useParams } from 'react-router-dom'

import { searchPermission } from '../../helpers/functions'
import { Colors } from '../../layout/Colors'
import { eventMonitoring } from '../../libs/monitoring/sentry'
import {
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../providers/apiHelpers'
import { dataProvider } from '../../providers/dataProvider'

import { BeneficiaryBadge } from './Components/BeneficiaryBadge'
import { FraudCheckCard } from './Components/FraudCheckCard'
import { ManualReviewModal } from './Components/ManualReviewModal'
import { StatusBadge } from './Components/StatusBadge'
import { UserDetailsCard } from './Components/UserDetailsCard'
import { UserHistoryCard } from './Components/UserHistoryCard'
import {
  EligibilityFraudCheck,
  EligibilitySubscriptionItem,
  PermissionsEnum,
  PublicUserRolesEnum,
  UserBaseInfo,
} from './types'

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

const cardStyle = {
  maxWidth: '99vw',
  width: '100%',
  marginTop: '20px',
  padding: 30,
}

export const UserDetail = () => {
  useAuthenticated()
  const { permissions } = usePermissions()
  const formattedPermissions: PermissionsEnum[] = permissions
  const canReviewPublicUser = !!searchPermission(
    formattedPermissions,
    PermissionsEnum.reviewPublicAccount
  )
  const { id } = useParams() // this component is rendered in the /books/:id path
  const redirect = useRedirect()
  const [tabValue, setTabValue] = useState(1)

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }

  const { data: userBaseInfo, isLoading } = useGetOne<UserBaseInfo>(
    'public_accounts',
    { id: id as Identifier },
    // redirect to the list if the book is not found
    { onError: () => redirect('/public_users/search') }
  )

  const notify = useNotify()

  async function resendValidationEmail() {
    try {
      const response = await dataProvider.postResendValidationEmail(
        'public_accounts',
        userBaseInfo
      )
      const responseData = await response.json()
      if (response.code === 400) {
        notify(Object.values(responseData)[0] as string, { type: 'error' })
      }
    } catch (error) {
      if (error instanceof PcApiHttpError) {
        notify(getHttpApiErrorMessage(error), { type: 'error' })
      } else {
        notify('La confirmation a été envoyée avec succès', { type: 'success' })
      }
      captureException(error)
    }
  }

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

  let subscriptionItems: EligibilitySubscriptionItem[] = []
  let idsCheckHistory: EligibilityFraudCheck[] = []

  const idCheckHistoryLengthAge18 = AGE18?.idCheckHistory?.length
  const idCheckHistoryLengthUnderage = UNDERAGE?.idCheckHistory?.length

  if (idCheckHistoryLengthAge18 > 0 && idCheckHistoryLengthUnderage === 0) {
    idsCheckHistory.push({
      role: PublicUserRolesEnum.beneficiary,
      items: AGE18.idCheckHistory,
    })
    subscriptionItems.push({
      role: PublicUserRolesEnum.beneficiary,
      items: AGE18.subscriptionItems,
    })
  } else if (
    idCheckHistoryLengthUnderage > 0 &&
    idCheckHistoryLengthAge18 === 0
  ) {
    idsCheckHistory.push({
      role: PublicUserRolesEnum.underageBeneficiary,
      items: UNDERAGE.idCheckHistory,
    })
    subscriptionItems.push({
      role: PublicUserRolesEnum.underageBeneficiary,
      items: UNDERAGE.subscriptionItems,
    })
  } else if (
    idCheckHistoryLengthAge18 > 0 &&
    idCheckHistoryLengthUnderage > 0
  ) {
    idsCheckHistory.push(
      {
        role: PublicUserRolesEnum.beneficiary,
        items: AGE18.idCheckHistory,
      },
      {
        role: PublicUserRolesEnum.underageBeneficiary,
        items: UNDERAGE.idCheckHistory,
      }
    )
    subscriptionItems.push(
      { role: PublicUserRolesEnum.beneficiary, items: AGE18.subscriptionItems },
      {
        role: PublicUserRolesEnum.underageBeneficiary,
        items: UNDERAGE.subscriptionItems,
      }
    )
  } else {
    idsCheckHistory = []
    subscriptionItems = []
  }

  return (
    <Grid
      container
      spacing={0}
      direction="column"
      alignItems="center"
      justifyContent="center"
      sx={{ maxWidth: '99vw', width: '100%' }}
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
                <Button
                  variant={'outlined'}
                  onClick={resendValidationEmail}
                  size={'small'}
                  sx={{ mb: 2 }}
                >
                  Renvoyer l'email de validation
                </Button>
                <Typography variant="body1" gutterBottom component="div">
                  <strong>Tél : </strong>
                  {userBaseInfo.phoneNumber}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body1" gutterBottom component="div">
                  Crédité le :{' '}
                  {userBaseInfo.userCredit &&
                    userBaseInfo.userCredit.dateCreated &&
                    format(
                      parseISO(userBaseInfo.userCredit.dateCreated.toString()),
                      'dd/MM/yyyy'
                    )}
                </Typography>
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
                  Suspendre le compte
                </Button>
                {canReviewPublicUser && (
                  <ManualReviewModal
                    user={userBaseInfo}
                    eligibilityFraudChecks={idsCheckHistory}
                  />
                )}
              </Stack>
            </div>
          </Grid>
        </Grid>
      </Card>
      <Grid container spacing={1}>
        <Grid item xs={4}>
          <Card style={{ ...cardStyle, height: '9rem' }}>
            <Typography variant={'h5'} component={'div'}>
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
                {idsCheckHistory.length > 0 &&
                  idsCheckHistory[0].items.length > 0 &&
                  idsCheckHistory[0].items[0].type}
              </strong>{' '}
              importé le :{' '}
              {idsCheckHistory.length > 0 &&
                idsCheckHistory[0].items.length > 0 &&
                idsCheckHistory[0].items[0].dateCreated &&
                format(
                  parseISO(idsCheckHistory[0].items[0].dateCreated.toString()),
                  'dd/MM/yyyy'
                )}
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
            <Tab label="" {...a11yProps(0)} disabled />
            <Tab
              label="Informations Personnelles"
              {...a11yProps(1)}
              sx={{ bgcolor: alpha(Colors.GREY, 0.1) }}
            />
            <Tab label="" {...a11yProps(2)} disabled />
          </Tabs>
          <TabPanel value={tabValue} index={0}>
            Bientôt disponible
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <Stack spacing={4}>
              <Card style={cardStyle}>
                <Typography
                  variant={'body1'}
                  sx={{ color: Colors.GREY, mb: 4 }}
                >
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
                  <Grid item xs={3}>
                    <Link
                      role={'link'}
                      href={'#parcours-register'}
                      color={Colors.GREY}
                      variant="body2"
                    >
                      PARCOURS D'INSCRIPTION
                    </Link>
                  </Grid>
                  {idsCheckHistory.length > 0 &&
                    idsCheckHistory.map(idCheckHistory => (
                      <Grid item xs={4} key={idCheckHistory.role}>
                        {idCheckHistory.items.length > 0 &&
                          idCheckHistory.items.map(fraudCheck => (
                            <div
                              style={{ marginRight: '1rem' }}
                              key={fraudCheck.thirdPartyId}
                            >
                              <Link
                                role={'link'}
                                href={`#${fraudCheck.thirdPartyId}`}
                                color={Colors.GREY}
                                variant="body2"
                              >
                                {fraudCheck.type.toUpperCase()}
                              </Link>
                            </div>
                          ))}
                      </Grid>
                    ))}
                </Grid>
              </Card>
              <div id="details-user">
                {idsCheckHistory.length > 0 &&
                  idsCheckHistory[0].items.length > 0 && (
                    <UserDetailsCard
                      user={userBaseInfo}
                      firstFraudCheck={idsCheckHistory[0].items[0]}
                    />
                  )}
              </div>
              <div id="parcours-register">
                {subscriptionItems.map(subscriptionItem => (
                  <div key={subscriptionItem.role}>
                    <UserHistoryCard subscriptionItem={subscriptionItem} />
                  </div>
                ))}
              </div>
              {idsCheckHistory.length > 0 &&
                idsCheckHistory.map(idCheckHistory => (
                  <div key={idCheckHistory.role}>
                    {idCheckHistory.items.length > 0 &&
                      idCheckHistory.items.map(fraudCheck => (
                        <div
                          id={fraudCheck.thirdPartyId}
                          key={fraudCheck.thirdPartyId}
                        >
                          <FraudCheckCard
                            eligibilityFraudCheck={{
                              role: idCheckHistory.role,
                              items: [fraudCheck],
                            }}
                          />
                        </div>
                      ))}
                  </div>
                ))}
            </Stack>
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            Bientôt disponible
          </TabPanel>
        </Box>
      </Grid>
    </Grid>
  )
}
