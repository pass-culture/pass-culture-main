import { Card, Button, Grid, Stack, Tooltip, Typography } from '@mui/material'
import { captureException } from '@sentry/react'
import { format, parseISO } from 'date-fns'
import React, { useState } from 'react'
import { Form, useNotify, TextInput, SaveButton } from 'react-admin'
import { FieldValues } from 'react-hook-form'

import {
  getGenericHttpErrorMessage,
  getHttpApiErrorMessage,
  PcApiHttpError,
} from '../../../providers/apiHelpers'
import { apiProvider } from '../../../providers/apiProvider'
import {
  IdCheckItemModel,
  PublicAccount,
  UpdatePublicAccountRequest,
} from '../../../TypesFromApi'
import { FraudCheckTechnicalDetails } from '../types'

type Props = {
  user: PublicAccount
  firstFraudCheck: IdCheckItemModel
}
export const UserDetailsCard = ({ user, firstFraudCheck }: Props) => {
  const notify = useNotify()

  const [editable, setEditable] = useState(false)

  async function skipPhoneValidation() {
    try {
      const response = await apiProvider().skipPhoneValidation({
        userId: user.id,
      })
      if (response !== undefined) {
        notify('Le numéro de téléphone a été confirmé avec succès', {
          type: 'success',
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

  async function sendPhoneValidationCode() {
    try {
      const response = await apiProvider().sendPhoneValidationCode({
        userId: user.id,
      })
      if (response !== undefined) {
        notify('Le code de validation du téléphone a été envoyé avec succès', {
          type: 'success',
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

  const cardStyle = {
    width: '100%',
    marginTop: '20px',
    padding: 30,
  }

  const submitForm = async (params: FieldValues) => {
    if (params && user.id) {
      try {
        const request: UpdatePublicAccountRequest = {
          userId: user.id,
          publicAccountUpdateRequest: {
            address: params.address as string,
            city: params.city as string,
            dateOfBirth: parseISO(params.dateOfBirth.toString()) as Date,
            email: params.email as string,
            firstName: params.firstName as string,
            idPieceNumber:
              params.idPieceNumber !== '' ? params.idPieceNumber : null,
            lastName: params.lastName,
            phoneNumber: params.phoneNumber,
            postalCode: params.postalCode,
          },
        }
        setEditable(false)

        const response = await apiProvider().updatePublicAccount(request)
        if (response) {
          notify('Les modifications ont été appliquées avec succès', {
            type: 'success',
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
  }

  function toggleEditableForm() {
    setEditable(!editable)
  }

  return (
    <>
      <Card style={cardStyle}>
        <Form onSubmit={submitForm}>
          <Typography variant={'h5'}>Détails utilisateur </Typography>
          <Grid container sx={{ mt: 4 }}>
            <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
              <Grid item xs={4}>
                <TextInput
                  id="user-lastname"
                  type={'text'}
                  label="Nom"
                  variant="standard"
                  defaultValue={user.lastName}
                  source={'lastName'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={4}>
                <TextInput
                  id="user-firstname"
                  type={'text'}
                  label="Prénom"
                  variant="standard"
                  defaultValue={user.firstName}
                  source={'firstName'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={4}>
                {user.email && (
                  <>
                    <TextInput
                      source={'email'}
                      id="user-email"
                      label="E-mail"
                      variant="standard"
                      defaultValue={user.email}
                      disabled={!editable}
                      style={{ width: '100%' }}
                      type={'email'}
                    />
                  </>
                )}
              </Grid>
            </Stack>
            <Stack
              spacing={3}
              direction={'row'}
              style={{ width: '100%' }}
              sx={{ mt: 3 }}
            >
              <Grid item xs={4}>
                <Typography variant={'body1'}>Numéro de téléphone</Typography>
                <Typography variant={'body1'}>
                  {user.phoneNumber ? user.phoneNumber : ''}
                </Typography>

                <Stack
                  width={'60%'}
                  sx={{ mt: 2 }}
                  spacing={2}
                  textAlign={'left'}
                >
                  <Tooltip
                    title={
                      !user.phoneNumber
                        ? 'Veuillez renseigner le numéro de téléphone'
                        : ''
                    }
                    arrow
                  >
                    <div>
                      <Button
                        disabled={!user.phoneNumber}
                        variant="outlined"
                        onClick={sendPhoneValidationCode}
                      >
                        Envoyer un code de validation
                      </Button>
                    </div>
                  </Tooltip>
                  <Tooltip
                    title={
                      !user.phoneNumber
                        ? 'Veuillez renseigner le numéro de téléphone'
                        : ''
                    }
                  >
                    <div>
                      <Button
                        disabled={!user.phoneNumber}
                        variant="outlined"
                        onClick={skipPhoneValidation}
                        style={{ visibility: 'hidden' }}
                      >
                        Confirmer manuellement
                      </Button>
                    </div>
                  </Tooltip>
                </Stack>
              </Grid>
              <Grid item xs={4}>
                <TextInput
                  id={'user-date-birth'}
                  source={'dateOfBirth'}
                  label={'Date de naissance'}
                  defaultValue={
                    user.dateOfBirth
                      ? format(user.dateOfBirth as Date, 'yyyy-MM-dd')
                      : ''
                  }
                  disabled={!editable}
                  variant={'standard'}
                  type={'date'}
                />
              </Grid>
              <Grid item xs={4}>
                <Typography variant={'body1'}>
                  Date de création du compte :
                </Typography>

                <Typography variant={'body1'}>
                  {firstFraudCheck && firstFraudCheck.dateCreated
                    ? format(firstFraudCheck.dateCreated as Date, 'dd/MM/yyyy')
                    : 'N/A'}
                </Typography>
              </Grid>
            </Stack>
            <Stack
              spacing={3}
              direction={'row'}
              sx={{ mt: 3 }}
              style={{ width: '100%' }}
            >
              <Grid item xs={3}>
                <TextInput
                  id={'user-id-number'}
                  type={'text'}
                  label={'N° pièce d’identité'}
                  variant={'standard'}
                  defaultValue={
                    firstFraudCheck &&
                    firstFraudCheck.technicalDetails &&
                    (
                      firstFraudCheck.technicalDetails as FraudCheckTechnicalDetails
                    ).identificationId
                      ? (
                          firstFraudCheck.technicalDetails as FraudCheckTechnicalDetails
                        ).identificationId
                      : ''
                  }
                  source={'idPieceNumber'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={3}>
                <TextInput
                  id="user-address"
                  type={'text'}
                  label="Adresse"
                  variant="standard"
                  defaultValue={user.address}
                  source={'address'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={2}>
                <TextInput
                  id="user-postal-code"
                  type={'text'}
                  label="CP"
                  variant="standard"
                  defaultValue={user.postalCode}
                  source={'postalCode'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={2}>
                <TextInput
                  id="user-city"
                  type={'text'}
                  label="Ville"
                  variant="standard"
                  defaultValue={user.city}
                  source={'city'}
                  disabled={!editable}
                />
              </Grid>
            </Stack>
            <Stack
              spacing={3}
              direction={'row-reverse'}
              style={{ width: '100%' }}
            >
              {!editable ? (
                <>
                  <Button type={'button'} onClick={toggleEditableForm}>
                    Modifier les informations
                  </Button>
                </>
              ) : (
                <>
                  <SaveButton label={'Sauvegarder'} sx={{ mr: 3 }} />
                  <Button type={'button'} onClick={toggleEditableForm}>
                    Annuler{' '}
                  </Button>
                </>
              )}
            </Stack>
          </Grid>
        </Form>
      </Card>
    </>
  )
}
