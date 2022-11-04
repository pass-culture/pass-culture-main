import {
  Backdrop,
  Button,
  Card,
  CircularProgress,
  FormControl,
  InputLabel,
  Link,
  MenuItem,
  OutlinedInput,
  Select,
  SelectChangeEvent,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  Theme,
  Typography,
} from '@mui/material'
import { captureException } from '@sentry/react'
import { format } from 'date-fns'
import React, { useCallback, useEffect, useState } from 'react'
import {
  Form,
  TextInput,
  useAuthenticated,
  useNotify,
  usePermissions,
} from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { searchPermission } from '../../../helpers/functions'
import { Colors } from '../../../layout/Colors'
import { theme } from '../../../layout/theme'
import {
  getGenericHttpErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../../providers/apiHelpers'
import { apiProvider } from '../../../providers/apiProvider'
import {
  OffererTagItem,
  OffererTagsResponseModel,
  OffererToBeValidated,
  ValidationStatus,
} from '../../../TypesFromApi'
import { PermissionsEnum } from '../../PublicUsers/types'
import { OfferersToValidateContextTableMenu } from '../Components/OfferersToValidateContextTableMenu'
import { ValidationStatusBadge } from '../Components/ValidationStatusBadge'
import { ProTypeEnum } from '../types'

const ITEM_HEIGHT = 48
const ITEM_PADDING_TOP = 8
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
}

function stopTypingOnSearch(event: {
  key: string
  stopPropagation: () => void
}) {
  if (event.key === 'Enter') {
    event.stopPropagation()
  }
}

function getStyles(name: string, items: string[], theme: Theme) {
  return {
    fontWeight:
      items.indexOf(name) === -1
        ? theme.typography.fontWeightRegular
        : theme.typography.fontWeightMedium,
  }
}

enum OffererStatus {
  NEW = 'Nouvelle',
  PENDING = 'En attente',
  VALIDATED = 'Validée',
  REJECTED = 'Rejetée',
}

export const OfferersToValidate = () => {
  useAuthenticated()
  const notify = useNotify()
  const [isLoading, setIsLoading] = useState(false)
  const [data, setData] = useState({
    offerers: [] as OffererToBeValidated[],
    total: 0,
    totalPages: 0,
  })
  const [currentPage, setCurrentPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = React.useState(10)
  const { permissions } = usePermissions()
  const formattedAuthorizations: PermissionsEnum[] = permissions
  const permissionGranted = !!searchPermission(
    formattedAuthorizations,
    PermissionsEnum.validateOfferer
  )

  const [searchParameter, setSearchParameter] = useState<string | undefined>()
  const [offererTags, setOffererTags] = useState([] as OffererTagItem[])
  const [requestOffererTags, setRequestOffererTags] = useState([] as string[])
  const [requestOffererStatus, setRequestOffererStatus] = useState(
    [] as string[]
  )

  async function getOffererTags() {
    try {
      const response: OffererTagsResponseModel =
        await apiProvider().getOfferersTagsList()
      if (response && response.data && response.data.length > 0) {
        setOffererTags(response.data)
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

  async function getOfferersToBeValidated(page: number) {
    try {
      const filters: { field: string; value: string[] }[] = []

      filters.push({ field: 'tags', value: requestOffererTags })
      filters.push({ field: 'status', value: requestOffererStatus })

      const response = await apiProvider().listOfferersToBeValidated({
        page: page + 1,
        perPage: rowsPerPage,
        sort: JSON.stringify([{ field: 'dateCreated', order: 'desc' }]),
        filter: JSON.stringify(filters),
        q: searchParameter || undefined,
      })
      if (response && response.data) {
        setData({
          offerers: response.data,
          total: response.total,
          totalPages: response.pages,
        })
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

  async function onChangePage(
    event: React.MouseEvent<HTMLButtonElement> | null,
    value: number
  ) {
    setCurrentPage(value)
  }

  const handleOffererTagChange = async (
    event: SelectChangeEvent<typeof requestOffererTags>
  ) => {
    setData({ offerers: [], total: 0, totalPages: 0 })
    const {
      target: { value },
    } = event
    await setRequestOffererTags(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value
    )
  }
  const handleOffererStatusChange = async (
    event: SelectChangeEvent<typeof requestOffererStatus>
  ) => {
    setData({ offerers: [], total: 0, totalPages: 0 })
    const {
      target: { value },
    } = event
    await setRequestOffererStatus(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value
    )
  }

  const onChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setCurrentPage(0)
  }
  const offererToValidateManagement = useCallback(async () => {
    setIsLoading(true)

    await getOfferersToBeValidated(currentPage)
    setIsLoading(false)
  }, [setIsLoading, getOfferersToBeValidated])

  const offererTagsList = useCallback(async () => {
    await getOffererTags()
  }, [getOffererTags])

  const formSubmit = useCallback(
    async (params: FieldValues) => {
      setSearchParameter(params.search)
      await offererToValidateManagement()
    },
    [setSearchParameter, offererToValidateManagement]
  )

  const onContextMenuChange = useCallback(() => {
    offererToValidateManagement()
  }, [offererToValidateManagement])

  useEffect(() => {
    offererToValidateManagement()
    offererTagsList()
  }, [
    rowsPerPage,
    searchParameter,
    requestOffererTags,
    requestOffererStatus,
    currentPage,
  ])

  return (
    <div>
      <Backdrop
        sx={{ color: '#fff', zIndex: theme => theme.zIndex.drawer + 1 }}
        open={isLoading}
      >
        <CircularProgress color="inherit" />
      </Backdrop>
      {permissionGranted && (
        <>
          <Card sx={{ padding: 2, mt: 5 }}>
            <Typography variant={'h4'} color={Colors.GREY}>
              Structures à valider
            </Typography>
            <Form onSubmit={formSubmit}>
              <Stack direction="row" spacing={2} style={{ marginTop: 10 }}>
                <FormControl sx={{ m: 1, width: 350 }}>
                  <TextInput
                    helperText={false}
                    source={'q'}
                    name={'search'}
                    type={'text'}
                    label={'Rechercher des structures par nom, SIREN'}
                    variant={'outlined'}
                    style={{
                      marginLeft: 0,
                      marginRight: 5,
                      width: 'auto',
                    }}
                    onKeyUp={stopTypingOnSearch}
                    InputProps={{}}
                  />
                </FormControl>
                <Button
                  type={'submit'}
                  variant="contained"
                  style={{ height: '2.5rem', marginTop: 8, marginBottom: 20 }}
                >
                  Chercher
                </Button>
              </Stack>
            </Form>
            <Stack direction="row" spacing={2}>
              <div>
                <FormControl sx={{ m: 1, width: 300 }}>
                  <InputLabel id="demo-multiple-name-label">Tags</InputLabel>
                  <Select
                    labelId="demo-multiple-name-label"
                    id="demo-multiple-name"
                    multiple
                    value={requestOffererTags}
                    onChange={handleOffererTagChange}
                    input={<OutlinedInput label="Name" />}
                    MenuProps={MenuProps}
                  >
                    {offererTags.map(tag => (
                      <MenuItem
                        key={tag.id}
                        value={tag.label ? tag.label : tag.name}
                        style={getStyles(
                          tag.label ? tag.label : tag.name,
                          requestOffererTags,
                          theme
                        )}
                      >
                        {tag.label ? tag.label : tag.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </div>
              <div>
                <FormControl sx={{ m: 1, width: 300 }}>
                  <InputLabel id="multiple-status-label">Statuts</InputLabel>
                  <Select
                    labelId="multiple-status-label"
                    id="multiple-status"
                    multiple
                    value={requestOffererStatus}
                    onChange={handleOffererStatusChange}
                    input={<OutlinedInput label="Status" />}
                    MenuProps={MenuProps}
                  >
                    {(
                      Object.keys(
                        OffererStatus
                      ) as (keyof typeof OffererStatus)[]
                    ).map(status => (
                      <MenuItem
                        key={status}
                        value={status}
                        style={getStyles(status, requestOffererStatus, theme)}
                      >
                        {OffererStatus[status]}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </div>
            </Stack>

            {data.total === 0 && (
              <>Aucune structure ne correspond à la requête</>
            )}
            {data.total > 0 && (
              <>
                <Table size="small" sx={{ mt: 3 }}>
                  <TableHead>
                    <TableRow>
                      <TableCell></TableCell>
                      <TableCell>ID</TableCell>
                      <TableCell>Nom de la structure</TableCell>
                      <TableCell>Statut</TableCell>
                      <TableCell>Top Acteur</TableCell>
                      <TableCell>Date de la demande</TableCell>
                      <TableCell>Dernier Commentaire</TableCell>
                      <TableCell>SIREN</TableCell>
                      <TableCell>Mail</TableCell>
                      <TableCell>Responsable Structure</TableCell>
                      <TableCell>Ville</TableCell>
                      <TableCell>Tél</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.offerers.map(offerer => (
                      <TableRow key={offerer.id}>
                        <TableCell>
                          <OfferersToValidateContextTableMenu
                            id={offerer.id}
                            onContextMenuChange={onContextMenuChange}
                          />
                        </TableCell>
                        <TableCell>{offerer.id}</TableCell>
                        <TableCell>
                          <Link
                            role={'link'}
                            href={`/offerer/${offerer.id}`}
                            color={Colors.GREY}
                          >
                            {offerer.name}
                          </Link>
                        </TableCell>
                        <TableCell>
                          {/*<Chip label={offerer.status} />*/}
                          <ValidationStatusBadge
                            status={offerer.status as ValidationStatus}
                            resourceType={ProTypeEnum.offerer}
                          />
                        </TableCell>
                        <TableCell>
                          <Switch
                            checked={offerer.isTopActor === true}
                            onChange={async () => {
                              try {
                                await apiProvider().toggleTopActor({
                                  offererId: offerer.id,
                                  isTopActorRequest: {
                                    isTopActor: !offerer.isTopActor,
                                  },
                                })
                                notify(
                                  'Le mise à jour a été effectuée avec succès !',
                                  { type: 'success' }
                                )
                                await getOfferersToBeValidated(currentPage)
                              } catch (error) {
                                if (error instanceof PcApiHttpError) {
                                  notify(getHttpApiErrorMessage(error), {
                                    type: 'error',
                                  })
                                } else {
                                  notify(
                                    await getGenericHttpErrorMessage(
                                      error as Response
                                    ),
                                    {
                                      type: 'error',
                                      messageArgs: (error as Response).status,
                                    }
                                  )
                                }
                                captureException(error)
                              }
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          {format(offerer.requestDate, 'dd/MM/yyyy')}
                        </TableCell>
                        <TableCell>
                          {offerer.lastComment && offerer.lastComment.content}
                        </TableCell>
                        <TableCell>
                          {offerer.siren && (
                            <Link
                              role={'link'}
                              href={`https://www.societe.com/cgi-bin/fiche?rncs=${encodeURIComponent(
                                offerer.siren
                              )}`}
                              target={'_blank'}
                              color={Colors.GREY}
                            >
                              {offerer.siren}
                            </Link>
                          )}
                        </TableCell>
                        <TableCell>{offerer.email}</TableCell>
                        <TableCell>
                          {offerer.ownerId && (
                            <>
                              <Link
                                role={'link'}
                                href={`/proUser/${offerer.ownerId}`}
                                color={Colors.GREY}
                              >
                                {offerer.owner}
                              </Link>
                            </>
                          )}
                        </TableCell>
                        <TableCell>{offerer.city}</TableCell>
                        <TableCell>{offerer.phoneNumber}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                  <TablePagination
                    count={data.total}
                    page={currentPage}
                    onPageChange={onChangePage}
                    rowsPerPage={rowsPerPage}
                    onRowsPerPageChange={onChangeRowsPerPage}
                    labelRowsPerPage={'Structures par page'}
                    labelDisplayedRows={({ from, to, count }) =>
                      from + ' à ' + to + ' sur ' + count
                    }
                  />
                </Table>
              </>
            )}
          </Card>
        </>
      )}
    </div>
  )
}
