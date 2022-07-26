import { Box, Button, Modal, Stack, Typography } from '@mui/material'
import { captureException } from '@sentry/react'
import * as React from 'react'
import { useState } from 'react'
import {
  Form,
  SaveButton,
  SelectInput,
  TextInput,
  useNotify,
} from 'react-admin'
import { FieldValues } from 'react-hook-form'

import { Colors } from '../../../layout/Colors'
import {
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../../providers/apiHelpers'
import { dataProvider } from '../../../providers/dataProvider'
import { ExclamationPointIcon } from '../../Icons/ExclamationPointIcon'
import { UserBaseInfo, UserManualReview, EligibilityFraudCheck } from '../types'

export const ManualReviewModal = ({
  user,
  eligibilityFraudChecks,
}: {
  user: UserBaseInfo
  eligibilityFraudChecks: EligibilityFraudCheck[]
}) => {
  const [openModal, setOpenModal] = useState(false)

  const fraudChecks = eligibilityFraudChecks.flatMap(
    eligibilityFraudCheck => eligibilityFraudCheck.items
  )
  const noFraudCheck = fraudChecks.length <= 0

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

  const statusChoices = [
    { id: 'OK', name: 'OK' },
    { id: 'KO', name: 'KO' },
    { id: 'REDIRECTED_TO_DMS', name: 'Renvoi vers DMS' },
  ]
  const eligibilityChoices = [
    { id: 'UNDERAGE', name: 'Pass 15-17', eligibility: 'UNDERAGE' },
    { id: 'AGE18', name: 'Pass 18 ans', eligibility: 'AGE18' },
  ]

  const handleOpenModal = () => {
    setOpenModal(!noFraudCheck)
  }
  const handleCloseModal = () => setOpenModal(false)

  const formSubmit = async (params: FieldValues) => {
    try {
      const formData: UserManualReview = {
        id: Number(user.id),
        review: params.review,
        reason: params.reason,
        eligibility: params.eligibility,
      }
      const response = await dataProvider.postUserManualReview(
        'public_accounts',
        formData
      )
      if (response && response.status === 200) {
        notify('La revue a été envoyée avec succès !', { type: 'success' })
        handleCloseModal()
      }
    } catch (error) {
      if (error instanceof PcApiHttpError) {
        notify(getHttpApiErrorMessage(error), { type: 'error' })
      } else {
        notify('Une erreur est survenue !', { type: 'error' })
      }
      handleCloseModal()
      captureException(error)
    }
  }

  return (
    <>
      <Button
        variant={'contained'}
        onClick={handleOpenModal}
        disabled={noFraudCheck}
      >
        {noFraudCheck
          ? 'Revue manuelle non disponible (aucun fraud check avec nom, prénom, date de naissance)'
          : 'Revue manuelle'}
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
              <Typography variant={'body2'} color={Colors.GREY} sx={{ mr: 6 }}>
                Nouveau statut
              </Typography>
              <SelectInput
                source="review"
                label={'Nouveau Statut'}
                fullWidth
                variant={'outlined'}
                choices={statusChoices}
              />
            </Stack>
            <Stack spacing={2} direction={'row'}>
              <Typography
                variant={'body2'}
                sx={{ mr: 8.6 }}
                color={Colors.GREY}
              >
                Éligibilité
              </Typography>
              <SelectInput
                source="eligibility"
                label={'Éligibilité'}
                variant={'outlined'}
                emptyText={'Par défaut'}
                emptyValue={null}
                fullWidth
                choices={eligibilityChoices}
                optionValue="eligibility"
              />
            </Stack>
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
              />
            </Stack>
            <Stack direction={'row-reverse'} spacing={3} sx={{ mt: 5 }}>
              <SaveButton label={'MODIFIER LE STATUT'} variant={'outlined'} />
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
