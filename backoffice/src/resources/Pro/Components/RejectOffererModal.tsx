import { Box, Button, MenuItem, Modal, Stack, Typography } from '@mui/material'
import { captureException } from '@sentry/react'
import * as React from 'react'
import { useState } from 'react'
import { Form, SaveButton, TextInput, useNotify } from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { Colors } from '../../../layout/Colors'
import {
  getGenericHttpErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../../providers/apiHelpers'
import { apiProvider } from '../../../providers/apiProvider'
import { RejectOffererRequest } from '../../../TypesFromApi'
import { ExclamationPointIcon } from '../../Icons/ExclamationPointIcon'

export const RejectOffererModal = ({
  offererId,
  onContextMenuChange,
}: {
  offererId: number
  onContextMenuChange: () => void
}) => {
  const [openModal, setOpenModal] = useState(false)
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

  const handleOpenModal = () => {
    setOpenModal(true)
  }
  const handleCloseModal = () => {
    setOpenModal(false)
    onContextMenuChange()
  }

  const formSubmit = async (params: FieldValues) => {
    try {
      const formData: RejectOffererRequest = {
        offererId: offererId,
        optionalCommentRequest: { comment: params.reason ? params.reason : '' },
      }
      await apiProvider().rejectOfferer(formData)
      notify('La revue a été envoyée avec succès !', { type: 'success' })
      handleCloseModal()
    } catch (error) {
      if (error instanceof PcApiHttpError) {
        notify(getHttpApiErrorMessage(error), { type: 'error' })
      } else {
        notify(await getGenericHttpErrorMessage(error as Response), {
          type: 'error',
        })
      }
      handleCloseModal()
      captureException(error)
    }
  }

  return (
    <>
      <MenuItem onClick={handleOpenModal}>Rejeter</MenuItem>
      <Modal
        open={openModal}
        onClose={handleCloseModal}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >
        <Box sx={styleModal}>
          <ExclamationPointIcon
            style={{
              display: 'flex',
              marginLeft: 'auto',
              marginRight: 'auto',
              marginBottom: '2rem',
            }}
          />
          <Form onSubmit={formSubmit}>
            <Stack spacing={2} direction={'row'}>
              <Typography color={Colors.GREY} variant={'body2'} sx={{ mr: 1 }}>
                Raison du changement
              </Typography>
              <TextInput
                label="Raison"
                source="reason"
                variant={'outlined'}
                fullWidth
                multiline
                rows={4}
                required={false}
              />
            </Stack>
            <Stack direction={'row-reverse'} spacing={3} sx={{ mt: 5 }}>
              <SaveButton
                label={'REJETER LA STRUCTURE'}
                variant={'outlined'}
                alwaysEnable={true}
              />
              <Button
                variant={'outlined'}
                onClick={handleCloseModal}
                color={'inherit'}
              >
                ANNULER LA MODIFICATION
              </Button>
            </Stack>
          </Form>
        </Box>
      </Modal>
    </>
  )
}
