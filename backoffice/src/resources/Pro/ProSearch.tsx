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
  Backdrop,
} from '@mui/material'
import { captureException } from '@sentry/react'
import React, { ClassAttributes, HTMLAttributes, useState } from 'react'
import {
  Form,
  TextInput,
  useAuthenticated,
  useNotify,
  usePermissions,
} from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { searchPermission } from '../../helpers/functions'
import { Colors } from '../../layout/Colors'
import {
  getGenericHttpErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../providers/apiHelpers'
import { apiProvider } from '../../providers/apiProvider'
import { ProResult, SearchProRequest } from '../../TypesFromApi'
import { CustomSearchIcon } from '../Icons/CustomSearchIcon'
import { StatusBadge } from '../PublicUsers/Components/StatusBadge'
import { PermissionsEnum } from '../PublicUsers/types'

import { ProTypeBadge } from './Components/ProTypeBadge'
import { ValidationStatusBadge } from './Components/ValidationStatusBadge'
import {
  isOfferer,
  isProUser,
  isVenue,
  Offerer,
  ProTypeEnum,
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

const ProCard = ({ record }: { record: ProResult }) => {
  const { id, resourceType, payload }: ProResult = record

  return (
    <Card sx={{ minWidth: 330 }}>
      <CardContent>
        <Stack direction={'row'} spacing={2} sx={{ mb: 2 }}>
          <ProTypeBadge type={resourceType as ProTypeEnum} resource={record} />
          {payload &&
            isProUser(payload as ProUser) &&
            !(payload as ProUser).isActive && (
              <>
                <StatusBadge active={(payload as ProUser).isActive} />
              </>
            )}
          {payload && isOfferer(payload as Offerer) && (
            <>
              <ValidationStatusBadge
                status={(payload as Offerer).validationStatus}
                resourceType={resourceType as ProTypeEnum}
              />
              {!(payload as Offerer).isActive && (
                <>
                  <StatusBadge
                    active={(payload as Offerer).isActive}
                    feminine={true}
                  />
                </>
              )}
            </>
          )}
          {payload && isVenue(payload as Venue) && (
            <>
              <ValidationStatusBadge
                status={(payload as Venue).validationStatus}
                resourceType={resourceType as ProTypeEnum}
              />
              {!(payload as Venue).isActive && (
                <>
                  <StatusBadge active={(payload as Venue).isActive} />
                </>
              )}
            </>
          )}
        </Stack>
        {payload && isProUser(payload as ProUser) && (
          <>
            <Typography variant="subtitle1" component="h4" align="left">
              {(payload as ProUser).firstName}{' '}
              <UpperCaseText>{(payload as ProUser).lastName}</UpperCaseText>
            </Typography>
            <Typography variant="subtitle2" component="h5" align="left">
              <Typography color={Colors.GREY}> ID : {record.id}</Typography>
            </Typography>
            <Typography variant="body2" align="left">
              <strong>E-mail</strong>: {(payload as ProUser).email}
            </Typography>
            <Typography variant="body2" align="left">
              <strong>Tél</strong>: {(payload as ProUser).phoneNumber}
            </Typography>
          </>
        )}
        {payload && isOfferer(payload as Offerer) && (
          <>
            <Typography variant="subtitle1" component="h4" align="left">
              <UpperCaseText>{(payload as Offerer).name}</UpperCaseText>
            </Typography>
            <Typography variant="subtitle2" component="h5" align="left">
              <Typography color={Colors.GREY}> ID : {record.id}</Typography>
            </Typography>
            <Typography variant="body2" align="left">
              <strong>SIREN</strong>: {(payload as Offerer).siren}
            </Typography>
          </>
        )}
        {payload && isVenue(payload as Venue) && (
          <>
            <Typography variant="subtitle1" component="h4" align="left">
              <UpperCaseText>{(payload as Venue).name}</UpperCaseText>
            </Typography>
            <Typography variant="subtitle2" component="h5" align="left">
              <Typography color={Colors.GREY}> ID : {record.id}</Typography>
            </Typography>
            <Typography variant="body2" align="left">
              <strong>E-mail</strong>: {(payload as Venue).email}
            </Typography>
            <Typography variant="body2" align="left">
              <strong>SIRET</strong>: {(payload as Venue).siret}
            </Typography>
          </>
        )}
      </CardContent>
      <CardActions>
        <Button
          href={`/${resourceType}/${id}`}
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

export const ProSearch = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [proDataState, setProDataState] = useState({
    proData: [] as ProResult[],
    total: 0,
    totalPages: 0,
  })
  const [proResource, setProResource] = React.useState('offerer')

  const [searchParameter, setSearchParameter] = useState('')
  const [emptyResults, setEmptyResults] = useState(true)
  useAuthenticated()
  const notify = useNotify()
  const { permissions } = usePermissions()
  const formattedAuthorizations: PermissionsEnum[] = permissions
  const permissionGranted = !!searchPermission(
    formattedAuthorizations,
    PermissionsEnum.searchProAccount
  )

  async function searchProList(searchParameter: string, page: number) {
    try {
      const searchProRequest = {
        q: searchParameter,
        type: proResource,
        page: page,
        perPage: 20,
      } as SearchProRequest

      const response = await apiProvider().searchPro(searchProRequest)

      if (response && response.data && response.data.length > 0) {
        setProDataState({
          proData: response.data,
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
        {permissionGranted && (
          <>
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
                <Grid
                  container
                  justifyContent={emptyResults ? 'center' : 'left'}
                >
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
              <Grid
                container
                spacing={2}
                sx={{ marginTop: '1em', minWidth: 275 }}
              >
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
          </>
        )}
        {!permissionGranted && (
          <>
            <Typography
              variant={'h5'}
              color={Colors.GREY}
              sx={{ mb: 3, mt: 3 }}
            >
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
    </>
  )
}
