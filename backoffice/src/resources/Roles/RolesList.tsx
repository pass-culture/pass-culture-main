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
  useRefresh,
  useTranslate,
} from 'react-admin'

import { Colors } from '../../layout/Colors'
import { theme } from '../../layout/theme'
import {
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../providers/apiHelpers'
import { dataProvider } from '../../providers/dataProvider'

import { AddRoleModal } from './Components/AddRoleModal'
import { Permission, Role } from './types'

export const RolesList = () => {
  useAuthenticated()

  const refresh = useRefresh()
  const notify = useNotify()

  const { data: roles, total: totalRoles } = useGetList<Role>('roles')
  const { data: permissions } = useGetList<Permission>('permissions')
  const rolesList: Role[] = roles ? roles : []
  const permissionsList: Permission[] = permissions ? permissions : []
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
      const role = rolesList.find(role => (role.id as Identifier) == roleId)
      if (role) {
        const response = await dataProvider.delete('roles', {
          id: role.id,
          previousData: role,
        })

        if (response.data) {
          refresh()
        }
      }
    } catch (error) {
      if (error instanceof PcApiHttpError) {
        notify(getHttpApiErrorMessage(error), { type: 'error' })
      } else {
        notify('Une erreur est survenue !', { type: 'error' })
      }
      captureException(error)
    }
  }

  const updateRole = async (role: Role, previousRole: Role) => {
    try {
      const previousRoleData = {
        name: previousRole.name,
        permissionIds: previousRole.permissions.map(
          permission => permission.id
        ),
      }

      const newRoleData = {
        name: role.name,
        permissionIds: role.permissions.map(permission => permission.id),
      }

      const response = await dataProvider.update('roles', {
        id: role.id,
        data: newRoleData,
        previousData: previousRoleData,
      })
      if (response.data) {
        notify('La modification du rôle a été effectuée avec succès', {
          type: 'success',
        })
        refresh()
      }
    } catch (error) {
      if (error instanceof PcApiHttpError) {
        notify(getHttpApiErrorMessage(error), { type: 'error' })
      } else {
        notify('Une erreur est survenue !', { type: 'error' })
      }
      captureException(error)
    }
  }

  const handleToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    const _role = rolesList.find(
      role => (role.id as Identifier) == (event.target.value as Identifier)
    )
    const _previousRole = _role
    const _permission = permissionsList.find(
      permission =>
        (permission.id as Identifier) == (event.target.name as Identifier)
    )
    if (_permission && _role && _previousRole) {
      if (event.target.checked) {
        _role.permissions.push(_permission)
      } else if (!event.target.checked) {
        _role.permissions = _role.permissions.filter(
          permission => permission.id.toString() != _permission.id.toString()
        )
      }
      updateRole(_role, _previousRole)
    }
  }
  return (
    <Grid container spacing={0} direction="column" sx={{ pt: 3 }}>
      <Typography variant={'h3'} color={Colors.GREY} sx={{ mb: 3, mt: 3 }}>
        {translate('menu.roleManagement', {
          smart_count: 2,
        })}
      </Typography>
      {permissions && <AddRoleModal permissions={permissions} />}
      {totalRoles &&
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
                {permissions?.map((permission: Permission) => {
                  return managePermissions(role, permission)
                })}
              </Grid>
            </AccordionDetails>
          </Accordion>
        ))}
    </Grid>
  )
}
