import {
  Box,
  Button,
  Divider,
  Grid,
  Modal,
  Stack,
  Typography,
} from '@mui/material'
import { captureException } from '@sentry/react'
import { useState } from 'react'
import {
  Form,
  TextInput,
  required,
  SaveButton,
  useRefresh,
  SelectArrayInput,
  CreateResult,
  CreateParams,
  useNotify,
} from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { Colors } from '../../../layout/Colors'
import {
  getErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../../providers/apiHelpers'
import { dataProvider } from '../../../providers/dataProvider'
import { Permission, Role, RoleRequest } from '../types'

export const AddRoleModal = ({
  permissions,
}: {
  permissions: Permission[]
}) => {
  const [openModal, setOpenModal] = useState(false)
  const refresh = useRefresh()
  const notify = useNotify()
  const styleModal = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 800,
    height: 600,
    bgcolor: 'background.paper',
    border: `1px solid ${Colors.GREY}`,
    borderRadius: '5px',
    boxShadow: 24,
    p: 4,
  }

  const handleOpenModal = () => setOpenModal(true)
  const handleCloseModal = () => setOpenModal(false)
  const formSubmit = async (params: FieldValues) => {
    if (params && permissions) {
      try {
        const formData: CreateParams<RoleRequest> = {
          data: {
            name: params.name,
            permissionIds: params.permissions,
          },
        }

        const response: CreateResult<Role> = await dataProvider.create(
          'roles',
          formData
        )
        if (response.data) {
          notify('Le rôle a été créé avec succès', {
            type: 'success',
          })
          refresh()
          handleCloseModal()
        }
      } catch (error) {
        if (error instanceof PcApiHttpError) {
          notify(getHttpApiErrorMessage(error), { type: 'error' })
        } else {
          notify(getErrorMessage('errors.api.generic'), { type: 'error' })
        }
        handleCloseModal()
        captureException(error)
      }
    }
  }

  return (
    <>
      <Grid container spacing={2}>
        <Grid item xs={4}>
          <Button variant={'contained'} onClick={handleOpenModal}>
            Ajouter un rôle
          </Button>
        </Grid>
      </Grid>

      <Modal
        open={openModal}
        onClose={handleCloseModal}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={{ ...styleModal, pt: 10 }}>
          <Form onSubmit={formSubmit}>
            <Stack spacing={2} sx={{ mb: 5 }}>
              <Typography variant={'h4'} color={Colors.GREY}>
                Ajouter un rôle
              </Typography>
            </Stack>
            <Stack spacing={2} direction={'row'}>
              <Typography color={Colors.GREY} variant={'body2'} sx={{ mr: 8 }}>
                Nom
              </Typography>
              <TextInput
                label="Nom"
                source="name"
                variant={'outlined'}
                fullWidth
                validate={[required()]}
              />
            </Stack>
            <Stack spacing={2} direction={'row'}>
              <Typography color={Colors.GREY} variant={'body2'} sx={{ mr: 2 }}>
                Permissions
              </Typography>
              <SelectArrayInput
                variant={'outlined'}
                fullWidth
                label={'Permissions'}
                source={'permissions'}
                name={'permissions'}
                choices={permissions}
              />
            </Stack>
            <Divider sx={{ my: 3 }} />
            <Stack spacing={2} direction={'row-reverse'}>
              <Button
                variant={'outlined'}
                onClick={handleCloseModal}
                sx={{ mr: 3 }}
              >
                Annuler
              </Button>
              <SaveButton label={'Enregistrer'} />
            </Stack>
          </Form>
        </Box>
      </Modal>
    </>
  )
}
