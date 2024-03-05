import { FormikProvider, useFormik } from 'formik'
import { useLocation, useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetVenueResponseModel } from 'apiClient/v1'
import Callout from 'components/Callout/Callout'
import { Events } from 'core/FirebaseEvents/constants'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { PartnerPageIndividualSection } from 'pages/Home/Offerers/PartnerPageIndividualSection'

import { serializeEditVenueBodyModel } from './serializers'
import { VenueEditionFormValues } from './types'
import { getValidationSchema } from './validationSchema'
import { VenueEditionForm } from './VenueEditionForm'
import styles from './VenueEditionFormScreen.module.scss'

interface VenueEditionProps {
  initialValues: VenueEditionFormValues
  venue: GetVenueResponseModel
}

export const VenueEditionFormScreen = ({
  initialValues,
  venue,
}: VenueEditionProps): JSX.Element => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const { currentUser } = useCurrentUser()

  const onSubmit = async (values: VenueEditionFormValues) => {
    try {
      await api.editVenue(
        venue.id,
        serializeEditVenueBodyModel(values, !venue.siret)
      )

      navigate('/accueil')

      if (currentUser.isAdmin) {
        notify.success(PATCH_SUCCESS_MESSAGE)
      }

      logEvent?.(Events.CLICKED_SAVE_VENUE, {
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
        venueLabelId: 'venueLabel',
        'contact.email': 'email',
        'contact.phoneNumber': 'phoneNumber',
        'contact.website': 'webSite',
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
        isEdition: true,
      })
    }
  }

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmit,
    validationSchema: getValidationSchema(venue.isVirtual),
  })

  return (
    <>
      {venue.isPermanent && (
        <>
          <Callout title="Les informations que vous renseignez ci-dessous sont affichées dans votre page partenaire, visible sur l’application pass Culture" />
          <PartnerPageIndividualSection
            venueId={venue.id}
            isVisibleInApp={Boolean(venue.isVisibleInApp)}
          />
        </>
      )}

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit} className={styles['venue-form']}>
          <VenueEditionForm venue={venue} />
        </form>
      </FormikProvider>
    </>
  )
}
