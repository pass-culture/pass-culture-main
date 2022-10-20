import { FormikProvider, useFormik } from 'formik'
import React, { useState } from 'react'
import { useHistory } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'components/hooks/useNotification'
import { IOfferer } from 'core/Offerers/types'
import { IProviders, IVenue } from 'core/Venue/types'
import useCurrentUser from 'hooks/useCurrentUser'
import {
  IVenueFormValues,
  validationSchema,
  VenueForm,
} from 'new_components/VenueForm'
import { Title } from 'ui-kit'

import {
  serializeEditVenueBodyModel,
  serializePostVenueBodyModel,
} from './serializers'
import style from './VenueFormScreen.module.scss'

interface IVenueEditionProps {
  isCreatingVenue: boolean
  initialValues: IVenueFormValues
  offerer: IOfferer
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  providers?: IProviders[]
  venueProviders?: VenueProviderResponse[]
  venue?: IVenue
}

const VenueFormScreen = ({
  isCreatingVenue,
  initialValues,
  offerer,
  venueTypes,
  venueLabels,
  venueProviders,
  venue,
  providers,
}: IVenueEditionProps): JSX.Element => {
  const history = useHistory()
  const notify = useNotification()
  const { currentUser } = useCurrentUser()
  const [isSiretValued, setIsSiretValued] = useState(
    isCreatingVenue || !!venue?.siret
  )

  const onSubmit = async (value: IVenueFormValues) => {
    const request = isCreatingVenue
      ? api.postCreateVenue(
          serializePostVenueBodyModel(value, {
            hideSiret: !isSiretValued,
            offererId: offerer.id,
          })
        )
      : api.editVenue(
          venue?.id || '',
          serializeEditVenueBodyModel(value, { hideSiret: !!venue?.comment })
        )

    request
      .then(() => {
        notify.success('Vos modifications ont bien été enregistrées')
        history.push(
          currentUser.isAdmin ? `/structures/${offerer.id}` : '/accueil'
        )
      })
      .catch(error => {
        let formErrors
        if (isErrorAPIError(error)) {
          formErrors = error.body
        }
        const apiFieldsMap: Record<string, string> = {
          venue: 'venueId',
        }

        if (!formErrors || Object.keys(formErrors).length === 0) {
          notify.error('Erreur inconnue lors de la sauvegarde du lieu.')
        } else {
          notify.error(
            'Une ou plusieurs erreurs sont présentes dans le formulaire'
          )
          formik.setErrors(serializeApiErrors(formErrors, apiFieldsMap))
          formik.setSubmitting(true)
        }
      })
  }

  /*const generateSiretOrCommentValidationSchema: any = useMemo(
    () => generateSiretValidationSchema(offerer.siren, isSiretValued),
    [offerer.siren, isSiretValued]
  )

  const formValidationSchema = validationSchema.concat(
    generateSiretOrCommentValidationSchema
  )*/

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmit,
    validationSchema: validationSchema, // FIXME: Should use formValidationSchema instead
  })

  return (
    <div>
      <Title level={1} className={style['venue-form-heading']}>
        {isCreatingVenue ? 'Création d’un lieu' : 'Lieu'}
      </Title>
      {!isCreatingVenue && (
        <Title level={2} className={style['venue-form-heading']}>
          {
            /* istanbul ignore next: DEBT, TO FIX */
            initialValues.publicName || initialValues.name
          }
        </Title>
      )}

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <VenueForm
            isCreatingVenue={isCreatingVenue}
            updateIsSiretValued={setIsSiretValued}
            venueTypes={venueTypes}
            venueLabels={venueLabels}
            venueProvider={venueProviders}
            provider={providers}
            venue={venue}
            offerer={offerer}
          />
        </form>
      </FormikProvider>
    </div>
  )
}

export default VenueFormScreen
