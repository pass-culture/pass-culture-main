import { FormikProvider, useFormik } from 'formik'
import { useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetOffererResponseModel } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { VenueCreationFormValues } from 'pages/VenueCreation/types'
import { validationSchema } from 'pages/VenueCreation/validationSchema'
import { VenueCreationForm } from 'pages/VenueCreation/VenueCreationForm'
import { Title } from 'ui-kit'

import { serializePostVenueBodyModel } from './serializers'
import { generateSiretValidationSchema } from './SiretOrCommentFields/validationSchema'
import style from './VenueCreationFormScreen.module.scss'
import { venueSubmitRedirectUrl } from './venueSubmitRedirectUrl'

interface VenueEditionProps {
  initialValues: VenueCreationFormValues
  offerer: GetOffererResponseModel
  venueTypes: SelectOption[]
}

export const VenueCreationFormScreen = ({
  initialValues,
  offerer,
  venueTypes,
}: VenueEditionProps): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const [isSiretValued, setIsSiretValued] = useState(true)

  const { logEvent } = useAnalytics()

  const { currentUser } = useCurrentUser()

  const onSubmit = async (values: VenueCreationFormValues) => {
    try {
      await api.postCreateVenue(
        serializePostVenueBodyModel(values, offerer.id, !isSiretValued)
      )

      navigate(venueSubmitRedirectUrl(offerer.id, currentUser))

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
        venueTypeCode: 'venueType',
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
            offerer={offerer}
          />
        </form>
      </FormikProvider>
    </div>
  )
}
