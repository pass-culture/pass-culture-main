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
  CircularProgress,
  Backdrop,
} from '@mui/material'
import { captureException } from '@sentry/react'
import React, { ClassAttributes, HTMLAttributes, useState } from 'react'
import { Form, TextInput, useAuthenticated, useNotify } from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { Colors } from '../../layout/Colors'
import {
  getGenericHttpErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../providers/apiHelpers'
import { apiProvider } from '../../providers/apiProvider'
import { PublicAccount, SearchPublicAccountRequest } from '../../TypesFromApi'
import { CustomSearchIcon } from '../Icons/CustomSearchIcon'

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

const UserCard = ({ record }: { record: PublicAccount }) => {
  const {
    id,
    email,
    roles,
    isActive,
    firstName,
    lastName,
    phoneNumber,
  }: PublicAccount = record
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
  const [isLoading, setIsLoading] = useState(false)
  const [userDataState, setUserDataState] = useState({
    userData: [] as PublicAccount[],
    total: 0,
    totalPages: 0,
  })
  const [searchParameter, setSearchParameter] = useState('')
  const [emptyResults, setEmptyResults] = useState(true)
  useAuthenticated()
  const notify = useNotify()

  async function searchPublicUserList(searchParameter: string, page: number) {
    try {
      const request: SearchPublicAccountRequest = {
        q: searchParameter,
        page: page,
        perPage: 20,
      }
      const response = await apiProvider().searchPublicAccount(request)
      if (response && response.data && response.data.length > 0) {
        setUserDataState({
          userData: response.data,
          total: response.total,
          totalPages: response.pages,
        })
        setEmptyResults(false)
      }
    } catch (error) {
      if (error instanceof PcApiHttpError) {
        notify(getHttpApiErrorMessage(error), { type: 'error' })
      } else {
        notify(await getGenericHttpErrorMessage(error as Response), {
          type: 'error',
        })
      }
      captureException(error)
    }
  }

  async function onChangePage(event: React.ChangeEvent<unknown>, page: number) {
    setIsLoading(true)
    await searchPublicUserList(searchParameter, page)
    setIsLoading(false)
  }

  async function formSubmit(params: FieldValues) {
    setIsLoading(true)
    if (params && params.search) {
      setSearchParameter(params.search)
      setUserDataState({
        userData: [],
        total: 0,
        totalPages: 0,
      })
      setEmptyResults(true)
      await searchPublicUserList(params.search, 1)
    }
    setIsLoading(false)
  }

  const clearSearch = () => {
    setUserDataState({
      userData: [],
      total: 0,
      totalPages: 0,
    })
    setEmptyResults(true)
  }

  return (
    <>
      {/* <CircularProgress
        size={250}
        thickness={2}
        style={{
          display: isLoading ? 'block' : 'none',
          marginTop: '3rem',
          marginLeft: 'auto',
          marginRight: 'auto',
        }}
      />*/}
      <Backdrop
        sx={{ color: '#fff', zIndex: theme => theme.zIndex.drawer + 1 }}
        open={isLoading}
      >
        <CircularProgress color="inherit" />
      </Backdrop>
      <Grid
        visibility={isLoading ? 'hidden' : 'visible'}
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
            {!emptyResults && <div>{userDataState.total} résultat(s)</div>}
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
    </>
  )
}
