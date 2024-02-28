import { FormikProvider, useFormik } from 'formik'
import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetOffererResponseModel, VenueProviderResponse } from 'apiClient/v1'
import { VenueFormValues } from 'components/VenueForm'
import { generateSiretValidationSchema } from 'components/VenueForm/Informations/SiretOrCommentFields'
import { validationSchema } from 'components/VenueForm/validationSchema'
import { VenueCreationForm } from 'components/VenueForm/VenueCreationForm'
import { Events } from 'core/FirebaseEvents/constants'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import { Providers } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { Title } from 'ui-kit'

import { serializePostVenueBodyModel } from './serializers'
import { venueSubmitRedirectUrl } from './utils/venueSubmitRedirectUrl'
import style from './VenueCreationFormScreen.module.scss'

interface VenueEditionProps {
  initialValues: VenueFormValues
  offerer: GetOffererResponseModel
  venueTypes: SelectOption[]
  providers?: Providers[]
  venueProviders?: VenueProviderResponse[]
}

export const VenueCreationFormScreen = ({
  initialValues,
  offerer,
  venueTypes,
  venueProviders,
  providers,
}: VenueEditionProps): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const [isSiretValued, setIsSiretValued] = useState(true)

  const { logEvent } = useAnalytics()

  const { currentUser } = useCurrentUser()

  const onSubmit = async (value: VenueFormValues) => {
    try {
      await api.postCreateVenue(
        serializePostVenueBodyModel(value, {
          hideSiret: !isSiretValued,
          offererId: offerer.id,
        })
      )

      navigate(venueSubmitRedirectUrl(true, offerer.id, currentUser))

      if (currentUser.isAdmin) {
        notify.success(PATCH_SUCCESS_MESSAGE)
      }

      logEvent?.(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: true,
        isEdition: false,
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
        notify.error('Erreur inconnue lors de la sauvegarde du lieu.')
      } else {
        notify.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )
        formik.setErrors(serializeApiErrors(formErrors, apiFieldsMap))
        formik.setStatus('apiError')
      }

      logEvent?.(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: false,
        isEdition: false,
      })
    }
  }

  const generateSiretOrCommentValidationSchema: any = useMemo(
    () => generateSiretValidationSchema(isSiretValued, offerer.siren),
    [offerer.siren, isSiretValued]
  )

  const formValidationSchema = validationSchema.concat(
    generateSiretOrCommentValidationSchema
  )

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmit,
    validationSchema: formValidationSchema,
  })

  return (
    <div>
      <div className={style['venue-form-heading']}>
        <div className={style['title-page']}>
          <Title level={1}>Création d’un lieu</Title>
        </div>
      </div>

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <VenueCreationForm
            updateIsSiretValued={setIsSiretValued}
            venueTypes={venueTypes}
            venueProvider={venueProviders}
            provider={providers}
            offerer={offerer}
          />
        </form>
      </FormikProvider>
    </div>
  )
}
