import { FormikProvider, useFormik } from 'formik'
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import {
  GetOffererResponseModel,
  GetVenueResponseModel,
  VenueProviderResponse,
  VenueTypeResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { SelectOption } from 'commons/custom_types/form'
import { useNotification } from 'commons/hooks/useNotification'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import fullBackIcon from 'icons/full-back.svg'
import { generateSiretValidationSchema } from 'pages/VenueSettings/SiretOrCommentFields/validationSchema'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { serializeEditVenueBodyModel } from './serializers'
import { VenueSettingsFormValues } from './types'
import { getValidationSchema } from './validationSchema'
import { VenueSettingsForm } from './VenueSettingsForm'
import styles from './VenueSettingsScreen.module.scss'

interface VenueSettingsScreenProps {
  initialValues: VenueSettingsFormValues
  offerer: GetOffererResponseModel
  venueLabels: SelectOption[]
  venueTypes: VenueTypeResponseModel[]
  venueProviders: VenueProviderResponse[]
  venue: GetVenueResponseModel
}

export const VenueSettingsScreen = ({
  initialValues,
  offerer,
  venueLabels,
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

  const onSubmit = async (values: VenueSettingsFormValues) => {
    try {
      await api.editVenue(
        venue.id,
        serializeEditVenueBodyModel(values, !venue.siret)
      )
      await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])

      navigate(`/structures/${venue.managingOfferer.id}/lieux/${venue.id}`)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: true,
        isEdition: true,
      })
    } catch (error) {
      let formErrors
      if (isErrorAPIError(error)) {
        formErrors = error.body
      }
      const apiFieldsMap: Record<string, string> = {
        venue: 'venueId',
        venueTypeCode: 'venueType',
        venueLabelId: 'venueLabel',
        'contact.email': 'email',
        'contact.phoneNumber': 'phoneNumber',
        'contact.website': 'webSite',
        address: 'search-addressAutocomplete',
        visualDisabilityCompliant: 'accessibility.visual',
        mentalDisabilityCompliant: 'accessibility.mental',
        motorDisabilityCompliant: 'accessibility.motor',
        audioDisabilityCompliant: 'accessibility.audio',
      }

      if (!formErrors || Object.keys(formErrors).length === 0) {
        notify.error('Erreur inconnue lors de la sauvegarde de la structure.')
      } else {
        notify.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )
        formik.setErrors(serializeApiErrors(formErrors, apiFieldsMap))
        formik.setStatus('apiError')
      }

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: false,
        isEdition: true,
      })
    }
  }
  const formValidationSchema = getValidationSchema(venue.isVirtual).concat(
    generateSiretValidationSchema(
      venue.isVirtual,
      isSiretValued,
      offerer.siren,
      initialValues.siret
    )
  )

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmit,
    validationSchema: formValidationSchema,
  })

  return (
    <>
      <Button
        variant={ButtonVariant.TERNARYPINK}
        icon={fullBackIcon}
        onClick={() => navigate(-1)}
      >
        Retour vers la page précédente
      </Button>

      <h1 className={styles['title']}>Paramètres généraux</h1>
      <MandatoryInfo />

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit} noValidate>
          <VenueSettingsForm
            updateIsSiretValued={setIsSiretValued}
            venueLabels={venueLabels}
            venueTypes={venueTypes}
            venueProviders={venueProviders}
            venue={venue}
            offerer={offerer}
          />
        </form>
      </FormikProvider>
    </>
  )
}
