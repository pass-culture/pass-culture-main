import ClearIcon from '@mui/icons-material/Clear'
import {
  Box,
  Button,
  Card,
  CardActions,
  Pagination,
  CardContent,
  Grid,
  IconButton,
  InputAdornment,
  List,
  Stack,
  Typography,
} from '@mui/material'
import { captureException } from '@sentry/react'
import { ClassAttributes, HTMLAttributes, useState } from 'react'
import { Form, TextInput, useAuthenticated, useNotify } from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { Colors } from '../../layout/Colors'
import {
  getErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../providers/apiHelpers'
import { dataProvider } from '../../providers/dataProvider'
import { CustomSearchIcon } from '../Icons/CustomSearchIcon'
import { UserApiResponse } from '../PublicUsers/types'

import { BeneficiaryBadge } from './Components/BeneficiaryBadge'
import { StatusBadge } from './Components/StatusBadge'

const UpperCaseText = (
  props: JSX.IntrinsicAttributes &
    ClassAttributes<HTMLSpanElement> &
    HTMLAttributes<HTMLSpanElement>
) => (
  <span
    {...props}
    style={{
      textTransform: 'uppercase',
    }}
  ></span>
)

const UserCard = ({ record }: { record: UserApiResponse }) => {
  const {
    id,
    email,
    roles,
    isActive,
    firstName,
    lastName,
    phoneNumber,
  }: UserApiResponse = record
  return (
    <Card sx={{ minWidth: 275 }}>
      <CardContent>
        <Stack direction={'row'} spacing={2} sx={{ mb: 2 }}>
          <StatusBadge active={isActive} />
          <BeneficiaryBadge role={roles[0]} />
        </Stack>
        <Typography variant="subtitle1" component="h4" align="left">
          {firstName} <UpperCaseText>{lastName}</UpperCaseText>
        </Typography>
        <Typography variant="subtitle2" component="h5" align="left">
          <Typography color={Colors.GREY}>User ID : {id}</Typography>
        </Typography>
        <Typography variant="body2" align="left">
          <strong>E-mail</strong>: {email}
        </Typography>
        <Typography variant="body2" align="left">
          <strong>Tél</strong>: {phoneNumber}
        </Typography>
      </CardContent>
      <CardActions>
        <Button
          href={`/public_accounts/${id}`}
          variant={'text'}
          color={'inherit'}
        >
          Consulter ce profil
        </Button>
      </CardActions>
    </Card>
  )
}

function stopTypingOnSearch(event: {
  key: string
  stopPropagation: () => void
}) {
  if (event.key === 'Enter') {
    event.stopPropagation()
  }
}

export const UserSearch = () => {
  const [userDataState, setUserDataState] = useState({
    userData: [],
    userTotal: 0,
    totalPages: 0,
  })
  const [searchParameter, setSearchParameter] = useState('')
  const [emptyResults, setEmptyResults] = useState(true)
  useAuthenticated()
  const notify = useNotify()

  async function searchPublicUserList(searchParameter: string, page: number) {
    try {
      const response = await dataProvider.searchList('public_accounts', {
        pagination: {
          page: page,
          perPage: 20,
        },
        meta: {
          search: searchParameter,
        },
      })
      if (response && response.data && response.data.length > 0) {
        setUserDataState({
          userData: response.data,
          userTotal: response.total,
          totalPages: response.totalPages,
        })
        setEmptyResults(false)
      }
    } catch (error) {
      if (error instanceof PcApiHttpError) {
        notify(getHttpApiErrorMessage(error), { type: 'error' })
      } else {
        notify(getErrorMessage('errors.api.generic'), { type: 'error' })
      }
      captureException(error)
    }
  }

  async function onChangePage(event: React.ChangeEvent<unknown>, page: number) {
    await searchPublicUserList(searchParameter, page)
  }

  async function formSubmit(params: FieldValues) {
    if (params && params.search) {
      setSearchParameter(params.search)
      setUserDataState({
        userData: [],
        userTotal: 0,
        totalPages: 0,
      })
      setEmptyResults(true)
      await searchPublicUserList(params.search, 1)
    }
  }

  const clearSearch = () => {
    setUserDataState({
      userData: [],
      userTotal: 0,
      totalPages: 0,
    })
    setEmptyResults(true)
  }

  return (
    <Grid
      container
      spacing={0}
      direction="column"
      alignItems="center"
      justifyContent="center"
    >
      <Card
        style={{
          boxShadow: 'none',
          width: '100%',
          marginLeft: 0,
          paddingTop: '20px',
        }}
      >
        <CardContent>
          <Typography
            component="div"
            textAlign={emptyResults ? 'center' : 'left'}
            style={{
              display: emptyResults ? 'block' : 'none',
              paddingTop: '7rem',
            }}
          >
            <CustomSearchIcon />
          </Typography>
          <Typography
            variant={'subtitle1'}
            component={'div'}
            mb={2}
            sx={emptyResults ? { mx: 'auto' } : { mx: 1 }}
            gutterBottom
            textAlign={emptyResults ? 'center' : 'left'}
            style={{
              width: '30rem',
              display: emptyResults ? 'block' : 'none',
            }}
          >
            Retrouve un utilisateur à partir de son nom, prénom, date de
            naissance, userID, numéro de téléphone ou son adresse email.
          </Typography>
          <Grid container justifyContent={emptyResults ? 'center' : 'left'}>
            <Box>
              <Form onSubmit={formSubmit}>
                <Stack
                  style={{
                    justifyContent: 'center',
                    alignItems: 'center',
                    textAlign: 'center',
                  }}
                  direction={emptyResults ? 'column' : 'row'}
                >
                  <TextInput
                    helperText={false}
                    source={'q'}
                    name={'search'}
                    type={'text'}
                    label={emptyResults ? '' : 'Recherche'}
                    variant={'outlined'}
                    style={{
                      marginLeft: 'auto',
                      marginRight: 5,
                      width: emptyResults ? '20rem' : 'auto',
                    }}
                    onKeyUp={stopTypingOnSearch}
                    InputProps={
                      !emptyResults
                        ? {
                            endAdornment: (
                              <InputAdornment position="start">
                                <IconButton
                                  aria-label={
                                    'Rechercher un utilisateur public'
                                  }
                                  onClick={clearSearch}
                                >
                                  <ClearIcon />
                                </IconButton>
                              </InputAdornment>
                            ),
                          }
                        : {}
                    }
                  />

                  <Button
                    type={'submit'}
                    variant="contained"
                    style={{ height: '2.5rem' }}
                  >
                    Chercher
                  </Button>
                </Stack>
              </Form>
            </Box>
          </Grid>
          {!emptyResults && <div>{userDataState.userTotal} résultat(s)</div>}
          {!emptyResults && (
            <Pagination
              count={userDataState.totalPages}
              onChange={onChangePage}
            />
          )}
        </CardContent>
      </Card>
      <List>
        <Grid container spacing={2} sx={{ marginTop: '1em', minWidth: 275 }}>
          {!emptyResults &&
            userDataState.userData.map(user => (
              <Grid
                key={user['id']}
                sx={{ minWidth: 275 }}
                xs={12}
                sm={6}
                md={4}
                lg={4}
                xl={4}
                item
              >
                <UserCard record={user} />
              </Grid>
            ))}
        </Grid>
      </List>
    </Grid>
  )
}
