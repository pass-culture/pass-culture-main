import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  Divider,
  FormControlLabel,
  FormGroup,
  Grid,
  Switch,
  Typography,
} from '@mui/material'
import { captureException } from '@sentry/react'
import {
  Identifier,
  useAuthenticated,
  useGetList,
  useNotify,
  usePermissions,
  useRefresh,
  useTranslate,
} from 'react-admin'

import { searchPermission } from '../../helpers/functions'
import { Colors } from '../../layout/Colors'
import { theme } from '../../layout/theme'
import {
  getGenericHttpErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../providers/apiHelpers'
import { apiProvider } from '../../providers/apiProvider'
import { Role, Permission } from '../../TypesFromApi'
import { PermissionsEnum } from '../PublicUsers/types'

import { AddRoleModal } from './Components/AddRoleModal'

export const RolesList = () => {
  useAuthenticated()

  const refresh = useRefresh()
  const notify = useNotify()
  const { permissions } = usePermissions()
  const formattedAuthorizations: PermissionsEnum[] = permissions

  const { data: roles, total: totalRoles } = useGetList<Role>('roles')
  const { data: _permissions } = useGetList<Permission>('permissions')
  const rolesList: Role[] = roles ? roles : []
  const permissionsList: Permission[] = _permissions ? _permissions : []
  const translate = useTranslate()

  const managePermissions = (role: Role, permission: Permission) => {
    let isChecked = false
    role.permissions.find(rolePermission => {
      if (rolePermission.id.toString() === permission.id.toString()) {
        isChecked = true
      }
    })

    return (
      <Grid item xs={4} sx={{ mr: 0 }} key={permission.id}>
        <FormGroup>
          <FormControlLabel
            control={
              <Switch
                checked={isChecked}
                value={role.id.toString()}
                name={permission.id.toString()}
                onChange={event => {
                  event.preventDefault()
                  handleToggle(event)
                }}
                key={permission.id}
              />
            }
            label={permission.name}
          />
        </FormGroup>
      </Grid>
    )
  }

  const deleteRole = async (roleId: Identifier) => {
    try {
      const role = rolesList.find(role => role.id == roleId)
      if (role) {
        const response = await apiProvider().deleteRole({
          id: role.id as number,
        })

        if (response) {
          refresh()
        }
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

  const updateRole = async (role: Role) => {
    try {
      const response = await apiProvider().updateRole({
        id: role.id,
        roleRequestModel: {
          name: role.name,
          permissionIds: role.permissions.map(permission => permission.id),
        },
      })
      if (response) {
        notify('La modification du rôle a été effectuée avec succès', {
          type: 'success',
        })
        refresh()
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

  const handleToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    const _role = rolesList.find(
      role => (role.id as Identifier) == (event.target.value as Identifier)
    )
    const _permission = permissionsList.find(
      permission =>
        (permission.id as Identifier) == (event.target.name as Identifier)
    )
    if (_permission && _role) {
      if (event.target.checked) {
        _role.permissions.push(_permission)
      } else if (!event.target.checked) {
        _role.permissions = _role.permissions.filter(
          permission => permission.id.toString() != _permission.id.toString()
        )
      }
      updateRole(_role)
    }
  }

  const permissionGranted = !!searchPermission(
    formattedAuthorizations,
    PermissionsEnum.managePermissions
  )

  return (
    <Grid container spacing={0} direction="column" sx={{ pt: 3 }}>
      <Typography variant={'h3'} color={Colors.GREY} sx={{ mb: 3, mt: 3 }}>
        {permissionGranted &&
          translate('menu.roleManagement', {
            smart_count: 2,
          })}
      </Typography>
      {permissionGranted && _permissions && (
        <AddRoleModal permissions={_permissions} />
      )}
      {permissionGranted &&
        totalRoles &&
        totalRoles > 0 &&
        rolesList.map((role: Role) => (
          <Accordion key={role.id} sx={{ mt: 3, boxShadow: theme.shadows[2] }}>
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls="panel1a-content"
              id="panel1a-header"
            >
              <Typography>{role.name}</Typography>
            </AccordionSummary>
            <Divider />
            <AccordionDetails sx={{ mt: 2 }}>
              <Button
                variant={'outlined'}
                onClick={() => deleteRole(role.id as Identifier)}
                size={'small'}
                sx={{ mb: 4 }}
              >
                Supprimer le role
              </Button>
              <Grid container spacing={2}>
                {_permissions?.map((permission: Permission) => {
                  return managePermissions(role, permission)
                })}
              </Grid>
            </AccordionDetails>
          </Accordion>
        ))}

      {!permissionGranted && (
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
