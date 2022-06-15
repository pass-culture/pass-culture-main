import { CheckHistory, UserBaseInfo } from './types'
import { Card } from '@material-ui/core'
import { Button, Grid, Stack, Tooltip, Typography } from '@mui/material'
import Moment from 'moment'
import React, { useState } from 'react'
import { dataProvider } from '../../providers/dataProvider'
import {
  Form,
  useNotify,
  TextInput,
  UpdateParams,
  SaveButton,
} from 'react-admin'
import { FieldValues } from 'react-hook-form'

export const UserDetailsCard = (
  user: UserBaseInfo,
  firstIdCheckHistory: CheckHistory
) => {
  const notify = useNotify()

  const [editable, setEditable] = useState(false)

  async function resendValidationEmail() {
    const response = await dataProvider.postResendValidationEmail(
      'public_accounts',
      user
    )
    const responseData = await response.json()
    if (response.code !== 200) {
      notify(Object.values(responseData)[0] as string, { type: 'error' })
    }
  }

  async function skipPhoneValidation() {
    const response = await dataProvider.postSkipPhoneValidation(
      'public_accounts',
      user
    )
    let responseData
    if (response.body) {
      responseData = await response.json()
    }
    if (response.code !== 204 && responseData) {
      notify(Object.values(responseData)[0] as string, { type: 'error' })
    } else if (response.code === 204 || response.ok) {
      notify('Le numéro de téléphone a été confirmé avec succès', {
        type: 'success',
      })
    }
  }

  async function sendPhoneValidationCode() {
    const response = await dataProvider.postPhoneValidationCode(
      'public_accounts',
      user
    )
    const responseData = await response.json()
    if (response.code !== 200) {
      notify(Object.values(responseData)[0] as string, { type: 'error' })
    } else if (response.code === 204) {
      notify('Un code a été envoyé au numéro de téléphone indiqué', {
        type: 'success',
      })
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
        console.log('params', params.lastName)
        const formData = {
          address: params.address,
          city: params.city,
          dateOfBirth: params.dateOfBirth,
          email: params.email,
          firstName: params.firstName,
          idPieceNumber: params.idPieceNumber,
          lastName: params.lastName,
          phoneNumer: params.phoneNumber,
          postalCode: params.postalCode,
        }
        const formParams: UpdateParams = {
          id: user.id,
          data: formData,
          previousData: user,
        }
        const response = await dataProvider.update(
          'public_accounts',
          formParams
        )
        const data = response.data
        console.log(data)
        setEditable(false)
      } catch (error) {
        throw error
      }
    }
  }

  function toggleEditableForm() {
    setEditable(true)
  }

  return (
    <>
      <Card style={cardStyle}>
        <Form onSubmit={submitForm}>
          <Typography variant={'h5'}>
            Détails utilisateur{' '}
            {!editable ? (
              <>
                <Button type={'button'} onClick={toggleEditableForm}>
                  Editer
                </Button>
              </>
            ) : (
              <SaveButton label={'Sauvegarder'} />
            )}
          </Typography>
          <Grid container spacing={1} sx={{ mt: 4 }}>
            <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
              <Grid item xs={4}>
                <p>Nom</p>
                <TextInput
                  id="user-lastname"
                  type={'text'}
                  label=""
                  variant="standard"
                  defaultValue={user.lastName}
                  source={'lastName'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={4}>
                <p>Prénom</p>
                <TextInput
                  id="user-firstname"
                  type={'text'}
                  label=""
                  variant="standard"
                  defaultValue={user.firstName}
                  source={'firstName'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={4}>
                <p>Email</p>
                {user.email && (
                  <>
                    <TextInput
                      source={'email'}
                      id="user-email"
                      label=""
                      variant="standard"
                      defaultValue={user.email}
                      disabled={!editable}
                      style={{ width: '100%' }}
                      type={'email'}
                    />

                    <Button
                      variant={'outlined'}
                      onClick={resendValidationEmail}
                    >
                      Renvoyer l'email de validation
                    </Button>
                  </>
                )}
              </Grid>
            </Stack>
            <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
              <Grid item xs={4}>
                <p>Numéro de téléphone</p>
                <TextInput
                  source={'phoneNumber'}
                  id="user-phone-number"
                  label=""
                  variant="standard"
                  defaultValue={user.phoneNumber ? user.phoneNumber : ''}
                  disabled={!editable}
                  style={{ width: '100%' }}
                />

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
                      >
                        Confirmer manuellement
                      </Button>
                    </div>
                  </Tooltip>
                </Stack>
              </Grid>
              <Grid item xs={4}>
                <p>Date de naissance</p>
                <TextInput
                  id={'user-date-birth'}
                  source={'dateOfBirth'}
                  label={''}
                  defaultValue={
                    user.dateOfBirth
                      ? Moment(user.dateOfBirth).format('YYYY-MM-D')
                      : ''
                  }
                  disabled={!editable}
                  style={{ width: '100%' }}
                  variant={'standard'}
                  type={'date'}
                />
              </Grid>
              <Grid item xs={4}>
                <p>Date de création du compte : </p>

                <p>
                  {firstIdCheckHistory && firstIdCheckHistory.dateCreated
                    ? Moment(firstIdCheckHistory.dateCreated).format(
                        'D/MM/YYYY à HH:mm'
                      )
                    : 'N/A'}
                </p>
              </Grid>
            </Stack>
            <Stack spacing={3} direction={'row'} style={{ width: '100%' }}>
              <Grid item xs={4}>
                <p>N&deg; de la pièce d’identité</p>
                <TextInput
                  id={'user-id-number'}
                  type={'text'}
                  label={''}
                  variant={'standard'}
                  defaultValue={
                    firstIdCheckHistory &&
                    firstIdCheckHistory.technicalDetails &&
                    firstIdCheckHistory.technicalDetails.identificationId
                      ? firstIdCheckHistory.technicalDetails.identificationId
                      : ''
                  }
                  source={'idPieceNumber'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={3}>
                <p>Adresse</p>
                <TextInput
                  id="user-address"
                  type={'text'}
                  label=""
                  variant="standard"
                  defaultValue={user.address}
                  source={'address'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={2}>
                <p>CP</p>
                <TextInput
                  id="user-postal-code"
                  type={'text'}
                  label=""
                  variant="standard"
                  defaultValue={user.postalCode}
                  source={'postalCode'}
                  disabled={!editable}
                />
              </Grid>
              <Grid item xs={3}>
                <p>Ville</p>
                <TextInput
                  id="user-city"
                  type={'text'}
                  label=""
                  variant="standard"
                  defaultValue={user.city}
                  source={'city'}
                  disabled={!editable}
                />
              </Grid>
            </Stack>
          </Grid>
        </Form>
      </Card>
    </>
  )
}
