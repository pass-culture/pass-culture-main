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
  TextField,
  MenuItem,
} from '@mui/material'
import { captureException } from '@sentry/react'
import React, { ClassAttributes, HTMLAttributes, useState } from 'react'
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

import { ProTypeBadge } from './Components/ProTypeBadge'
import {
  isOfferer,
  isProUser,
  isVenue,
  Offerer,
  ProResourceAPI,
  ProUser,
  Venue,
} from './types'

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

const proResources = [
  {
    value: 'offerer',
    label: 'Structure',
  },
  {
    value: 'venue',
    label: 'Lieu',
  },
  {
    value: 'proUser',
    label: 'Compte Pro',
  },
]

const ProCard = ({ record }: { record: ProResourceAPI }) => {
  const { id, resourceType, payload }: ProResourceAPI = record //TODO: implémenter le badge de status quand la valeur sera renvoyée depuis l'API

  return (
    <Card sx={{ minWidth: 275 }}>
      <CardContent>
        <Stack direction={'row'} spacing={2} sx={{ mb: 2 }}>
          <ProTypeBadge type={resourceType} resource={record} />
        </Stack>
        {payload && isProUser(payload) && (payload as ProUser) && (
          <>
            <Typography variant="subtitle1" component="h4" align="left">
              {payload.firstName}{' '}
              <UpperCaseText>{payload.lastName}</UpperCaseText>
            </Typography>
            <Typography variant="subtitle2" component="h5" align="left">
              <Typography color={Colors.GREY}> ID : {record.id}</Typography>
            </Typography>
            <Typography variant="body2" align="left">
              <strong>E-mail</strong>: {payload.email}
            </Typography>
            <Typography variant="body2" align="left">
              <strong>Tél</strong>: {payload.phoneNumber}
            </Typography>
          </>
        )}
        {payload && isOfferer(payload) && (payload as Offerer) && (
          <>
            <Typography variant="subtitle1" component="h4" align="left">
              <UpperCaseText>{payload.name}</UpperCaseText>
            </Typography>
            <Typography variant="subtitle2" component="h5" align="left">
              <Typography color={Colors.GREY}> ID : {record.id}</Typography>
            </Typography>
            <Typography variant="body2" align="left">
              <strong>SIREN</strong>: {payload.siren}
            </Typography>
          </>
        )}
        {payload && isVenue(payload) && (payload as Venue) && (
          <>
            <Typography variant="subtitle1" component="h4" align="left">
              <UpperCaseText>{payload.name}</UpperCaseText>
            </Typography>
            <Typography variant="subtitle2" component="h5" align="left">
              <Typography color={Colors.GREY}> ID : {record.id}</Typography>
            </Typography>
            <Typography variant="body2" align="left">
              <strong>E-mail</strong>: {payload.email}
            </Typography>
            <Typography variant="body2" align="left">
              <strong>SIRET</strong>: {payload.siret}
            </Typography>
          </>
        )}
      </CardContent>
      <CardActions>
        <Button
          href={`/${resourceType}/${id}`}
          variant={'text'}
          color={'inherit'}
          disabled
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

export const ProSearch = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [proDataState, setProDataState] = useState({
    proData: [],
    total: 0,
    totalPages: 0,
  })
  const [proResource, setProResource] = React.useState('offerer')

  const [searchParameter, setSearchParameter] = useState('')
  const [emptyResults, setEmptyResults] = useState(true)
  useAuthenticated()
  const notify = useNotify()

  async function searchProList(searchParameter: string, page: number) {
    try {
      const response = await dataProvider.searchList('pro', {
        pagination: {
          page: page,
          perPage: 20,
        },
        meta: {
          search: searchParameter,
          type: proResource,
        },
      })
      if (response && response.data && response.data.length > 0) {
        setProDataState({
          proData: response.data,
          total: response.total,
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
    setIsLoading(true)
    await searchProList(searchParameter, page)
    setIsLoading(false)
  }

  async function formSubmit(params: FieldValues) {
    setIsLoading(true)
    if (params && params.search) {
      setSearchParameter(params.search)
      setProDataState({
        proData: [],
        total: 0,
        totalPages: 0,
      })
      setEmptyResults(true)
      await searchProList(params.search, 1)
    }
    setIsLoading(false)
  }

  const clearSearch = () => {
    setProDataState({
      proData: [],
      total: 0,
      totalPages: 0,
    })
    setEmptyResults(true)
  }

  const handleChangeProResource = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setProResource(event.target.value)
  }
  return (
    <>
      <CircularProgress
        size={250}
        thickness={2}
        style={{
          display: isLoading ? 'block' : 'none',
          marginTop: '3rem',
          marginLeft: 'auto',
          marginRight: 'auto',
        }}
      />
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
              Retrouve une structure ou un lieu par raison sociale, SIREN,
              SIRET, ou par l’identité du pro (nom prénom, email rattaché au
              SIRET, numéro de tél )
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
                    <div style={{ marginBottom: 15 }}>
                      <TextField
                        id="outlined-select-currency"
                        select
                        label={emptyResults ? '' : 'Type'}
                        variant={'outlined'}
                        size={'small'}
                        value={proResource}
                        onChange={handleChangeProResource}
                        helperText=""
                        style={{
                          marginLeft: 'auto',
                          marginRight: 0,
                          width: 'auto',
                        }}
                      >
                        {proResources.map(option => (
                          <MenuItem key={option.value} value={option.value}>
                            {option.label}
                          </MenuItem>
                        ))}
                      </TextField>
                      <TextInput
                        helperText={false}
                        source={'q'}
                        name={'search'}
                        type={'text'}
                        label={emptyResults ? '' : 'Recherche'}
                        variant={'outlined'}
                        style={{
                          marginLeft: 0,
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
                                        'Rechercher un acteur culturel'
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
                    </div>
                    <Button
                      type={'submit'}
                      variant="contained"
                      style={{ height: '2.5rem', marginBottom: 20 }}
                    >
                      Chercher
                    </Button>
                  </Stack>
                </Form>
              </Box>
            </Grid>
            {!emptyResults && <div>{proDataState.total} résultat(s)</div>}
            {!emptyResults && (
              <Pagination
                count={proDataState.totalPages}
                onChange={onChangePage}
              />
            )}
          </CardContent>
        </Card>
        <List>
          <Grid container spacing={2} sx={{ marginTop: '1em', minWidth: 275 }}>
            {!emptyResults &&
              proDataState.proData.map(pro => (
                <Grid
                  key={pro['id']}
                  sx={{ minWidth: 275 }}
                  xs={12}
                  sm={6}
                  md={4}
                  lg={4}
                  xl={4}
                  item
                >
                  <ProCard record={pro} />
                </Grid>
              ))}
          </Grid>
        </List>
      </Grid>
    </>
  )
}
