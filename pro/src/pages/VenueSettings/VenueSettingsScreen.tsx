import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useNotification } from 'commons/hooks/useNotification'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { generateSiretValidationSchema } from 'pages/VenueSettings/SiretOrCommentFields/validationSchema'

import { serializeEditVenueBodyModel } from './serializers'
import { VenueSettingsFormValues } from './types'
import { getValidationSchema } from './validationSchema'
import { VenueSettingsForm } from './VenueSettingsForm'

interface VenueSettingsScreenProps {
  initialValues: VenueSettingsFormValues
  offerer: GetOffererResponseModel
  venueTypes: VenueTypeResponseModel[]
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsScreen = ({
  initialValues,
  offerer,
  venueTypes,
  venueProviders,
  venue,
}: VenueSettingsScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const [isSiretValued, setIsSiretValued] = useState(Boolean(venue.siret))
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()

  const formValidationSchema = getValidationSchema(venue.isVirtual).concat(
    generateSiretValidationSchema(
      venue.isVirtual,
      isSiretValued,
      offerer.siren,
      initialValues.siret
    )
  )

  const methods = useForm<VenueSettingsFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(formValidationSchema as any),
    mode: 'onBlur',
  })

  const onSubmit = async (values: VenueSettingsFormValues) => {
    try {
      await api.editVenue(
        venue.id,
        serializeEditVenueBodyModel(values, !venue.siret)
      )
      await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])

      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(`/structures/${venue.managingOfferer.id}/lieux/${venue.id}`)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: true,
        isEdition: true,
      })

      notify.success('Vos modifications ont été sauvegardées')
    } catch (error) {
      let formErrors
      if (isErrorAPIError(error)) {
        formErrors = error.body
      }

      const errorsKeys = Object.keys(formErrors)

      if (
        !formErrors ||
        errorsKeys.length === 0 ||
        errorsKeys.includes('global')
      ) {
        notify.error('Erreur lors de la sauvegarde de la structure.')
      } else {
        notify.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )

        for (const field of errorsKeys) {
          methods.setError(field as keyof VenueSettingsFormValues, {
            type: field,
            message: formErrors[field]?.toString(),
          })
        }
      }

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: false,
        isEdition: true,
      })
    }
  }

  return (
    <>
      <MandatoryInfo />
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)} noValidate>
          <VenueSettingsForm
            updateIsSiretValued={setIsSiretValued}
            venueTypes={venueTypes}
            venueProviders={venueProviders}
            venue={venue}
            offerer={offerer}
          />
        </form>
      </FormProvider>
    </>
  )
}
