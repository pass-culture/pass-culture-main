import {
  Backdrop,
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
import { useAuthenticated, useNotify, usePermissions } from 'react-admin'

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
  UserOffererToBeValidated,
  ValidationStatus,
} from '../../../TypesFromApi'
import { PermissionsEnum } from '../../PublicUsers/types'
import { OffererUsersToValidateContextTableMenu } from '../Components/OffererUsersToValidateContextTableMenu'
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

function getStyles(name: string, items: string[], theme: Theme) {
  return {
    fontWeight:
      items.indexOf(name) === -1
        ? theme.typography.fontWeightRegular
        : theme.typography.fontWeightMedium,
  }
}

enum UserOffererStatus {
  NEW = 'Nouveau',
  PENDING = 'En attente',
  VALIDATED = 'Validé',
  REJECTED = 'Rejeté',
}

export const UserOfferersToValidate = () => {
  useAuthenticated()
  const notify = useNotify()
  const [isLoading, setIsLoading] = useState(false)
  const [data, setData] = useState({
    userOfferers: [] as UserOffererToBeValidated[],
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

  const [requestUserOffererStatus, setRequestUserOffererStatus] = useState<
    string[]
  >([])

  async function getUserOfferersToBeValidated(page: number) {
    try {
      const filters: { field: string; value: string[] }[] = []

      filters.push({ field: 'status', value: requestUserOffererStatus })

      const response = await apiProvider().listOfferersAttachmentsToBeValidated(
        {
          page: page + 1,
          perPage: rowsPerPage,
          sort: JSON.stringify([{ field: 'id', order: 'desc' }]),
          filter: JSON.stringify(filters),
        }
      )
      if (response && response.data && response.data.length > 0) {
        setData({
          userOfferers: response.data,
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

  const handleOffererStatusChange = async (
    event: SelectChangeEvent<typeof requestUserOffererStatus>
  ) => {
    setData({ userOfferers: [], total: 0, totalPages: 0 })
    const {
      target: { value },
    } = event
    await setRequestUserOffererStatus(
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
  const userOffererToValidateManagement = useCallback(async () => {
    setIsLoading(true)

    await getUserOfferersToBeValidated(currentPage)
    setIsLoading(false)
  }, [setIsLoading, getUserOfferersToBeValidated])

  const onContextMenuChange = useCallback(() => {
    userOffererToValidateManagement()
  }, [userOffererToValidateManagement])

  useEffect(() => {
    userOffererToValidateManagement()
  }, [rowsPerPage, requestUserOffererStatus, currentPage])

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
              Rattachements à valider
            </Typography>
            <Stack direction="row" spacing={2}>
              <div>
                <FormControl sx={{ m: 1, width: 300 }}>
                  <InputLabel id="multiple-status-label">Statuts</InputLabel>
                  <Select
                    labelId="multiple-status-label"
                    id="multiple-status"
                    multiple
                    value={requestUserOffererStatus}
                    onChange={handleOffererStatusChange}
                    input={<OutlinedInput label="Status" />}
                    MenuProps={MenuProps}
                  >
                    {(
                      Object.keys(
                        UserOffererStatus
                      ) as (keyof typeof UserOffererStatus)[]
                    ).map(status => (
                      <MenuItem
                        key={status}
                        value={status}
                        style={getStyles(
                          status,
                          requestUserOffererStatus,
                          theme
                        )}
                      >
                        {UserOffererStatus[status]}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </div>
            </Stack>

            {data.total === 0 && (
              <>Aucun rattachement ne correspond à la requête</>
            )}
            {data.total > 0 && (
              <>
                <Table size="small" sx={{ mt: 3 }}>
                  <TableHead>
                    <TableRow>
                      <TableCell></TableCell>
                      <TableCell>ID Compte pro</TableCell>
                      <TableCell>Mail Compte pro</TableCell>
                      <TableCell>Nom Compte pro</TableCell>
                      <TableCell>Statut</TableCell>
                      <TableCell>Date de la demande</TableCell>
                      <TableCell>Dernier Commentaire</TableCell>
                      <TableCell>Tél Compte pro</TableCell>
                      <TableCell>Nom Structure</TableCell>
                      <TableCell>Date de création Structure</TableCell>
                      <TableCell>Email Responsable</TableCell>
                      <TableCell>SIREN</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.userOfferers.map(userOfferer => (
                      <TableRow key={userOfferer.id}>
                        <TableCell>
                          <OffererUsersToValidateContextTableMenu
                            id={userOfferer.id}
                            onContextMenuChange={onContextMenuChange}
                          />
                        </TableCell>
                        <TableCell>{userOfferer.userId}</TableCell>
                        <TableCell>{userOfferer.email}</TableCell>
                        <TableCell>
                          <Link
                            role={'link'}
                            href={`/proUser/${userOfferer.userId}`}
                            color={Colors.GREY}
                          >
                            {userOfferer.userName}
                          </Link>
                        </TableCell>
                        <TableCell>
                          {/*<Chip label={offerer.status} />*/}
                          <ValidationStatusBadge
                            status={userOfferer.status as ValidationStatus}
                            resourceType={ProTypeEnum.proUser}
                          />
                        </TableCell>
                        <TableCell>
                          {userOfferer.requestDate &&
                            format(userOfferer.requestDate, 'dd/MM/yyyy')}
                        </TableCell>
                        <TableCell>
                          {userOfferer.lastComment &&
                            userOfferer.lastComment.content}
                        </TableCell>
                        <TableCell>
                          {userOfferer.phoneNumber && userOfferer.phoneNumber}
                        </TableCell>
                        <TableCell>
                          <Link
                            role={'link'}
                            href={`/offerer/${userOfferer.offererId}`}
                            color={Colors.GREY}
                          >
                            {userOfferer.offererName}
                          </Link>
                        </TableCell>
                        <TableCell>
                          {userOfferer.offererCreatedDate &&
                            format(
                              userOfferer.offererCreatedDate,
                              'dd/MM/yyyy'
                            )}
                        </TableCell>
                        <TableCell>
                          {userOfferer.ownerId && (
                            <>
                              <Link
                                role={'link'}
                                href={`/proUser/${userOfferer.ownerId}`}
                                color={Colors.GREY}
                              >
                                {userOfferer.ownerEmail}
                              </Link>
                            </>
                          )}
                        </TableCell>
                        <TableCell>
                          {userOfferer.siren && (
                            <Link
                              role={'link'}
                              href={`https://www.societe.com/cgi-bin/fiche?rncs=${encodeURIComponent(
                                userOfferer.siren
                              )}`}
                              target={'_blank'}
                              color={Colors.GREY}
                            >
                              {userOfferer.siren}
                            </Link>
                          )}
                        </TableCell>
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
