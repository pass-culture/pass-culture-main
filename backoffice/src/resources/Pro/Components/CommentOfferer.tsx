import { Box, Button, Modal, Stack, Typography } from '@mui/material'
import { captureException } from '@sentry/react'
import { useCallback, useState } from 'react'
import * as React from 'react'
import { Form, SaveButton, TextInput, useNotify, useRefresh } from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { Colors } from '../../../layout/Colors'
import {
  getErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../../providers/apiHelpers'
import { apiProvider } from '../../../providers/apiProvider'
import { CommentOffererRequest } from '../../../TypesFromApi'
import { ExclamationPointIcon } from '../../Icons/ExclamationPointIcon'

type Props = {
  offererId: number
}
export const CommentOfferer = ({ offererId }: Props) => {
  const notify = useNotify()
  const [openModal, setOpenModal] = useState(false)

  const styleModal = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 800,
    height: 400,
    bgcolor: 'background.paper',
    border: `1px solid ${Colors.GREY}`,
    borderRadius: '5px',
    boxShadow: 24,
    p: 4,
  }

  const handleOpenModal = useCallback(() => {
    setOpenModal(true)
  }, [])

  const handleCloseModal = useCallback(() => {
    setOpenModal(false)
  }, [])

  const refresh = useRefresh()
  const formSubmit = async (params: FieldValues) => {
    try {
      const formData: CommentOffererRequest = {
        offererId: offererId,
        commentRequest: { comment: params.comment },
      }
      await apiProvider().commentOfferer(formData)

      notify('Le commentaire a été envoyé avec succès !', { type: 'success' })
      refresh()
      handleCloseModal()
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
  return (
    <>
      <Button
        variant={'text'}
        size={'small'}
        onClick={handleOpenModal}
        sx={{ mb: 3 }}
      >
        Ajouter un commentaire
      </Button>
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
                Commentaire interne pour l'offerer
              </Typography>
              <TextInput
                label="Commentaire"
                source="comment"
                variant={'outlined'}
                fullWidth
                multiline
                rows={4}
              />
            </Stack>
            <Stack direction={'row-reverse'} spacing={3} sx={{ mt: 5 }}>
              <SaveButton label={'COMMENTER'} variant={'outlined'} />
              <Button
                variant={'outlined'}
                onClick={handleCloseModal}
                color={'inherit'}
              >
                ANNULER LE COMMENTAIRE
              </Button>
            </Stack>
          </Form>
        </Box>
      </Modal>
    </>
  )
}
