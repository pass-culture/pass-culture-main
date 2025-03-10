import { Form, Formik, FormikConfig, FormikConsumer } from 'formik'
import { useLocation, useNavigate } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetVenueResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { AccessibilityForm } from './AccessibilityForm/AccessibilityForm'
import { OpeningHoursForm } from './OpeningHoursForm/OpeningHoursForm'
import { RouteLeavingGuardVenueEdition } from './RouteLeavingGuardVenueEdition'
import { serializeEditVenueBodyModel } from './serializers'
import { setInitialFormValues } from './setInitialFormValues'
import { VenueEditionFormValues } from './types'
import { getValidationSchema } from './validationSchema'
import { VenueFormActionBar } from './VenueFormActionBar/VenueFormActionBar'

interface VenueFormProps {
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({ venue }: VenueFormProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const isOpenToPublicEnabled = useActiveFeature('WIP_IS_OPEN_TO_PUBLIC')

  const onSubmit: FormikConfig<VenueEditionFormValues>['onSubmit'] = async (
    values,
    formikHelpers
  ) => {
    try {
      await api.editVenue(
        venue.id,
        serializeEditVenueBodyModel(
          values,
          !venue.siret,
          venue.openingHours !== null
        )
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
        notify.error('Erreur inconnue lors de la sauvegarde de la structure.')
      } else {
        notify.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )
        formikHelpers.setErrors(serializeApiErrors(formErrors, apiFieldsMap))
        formikHelpers.setStatus('apiError')
      }

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: false,
        isEdition: true,
      })
    }
  }

  const isAccessibilityDefinedViaAccesLibre = !!venue.externalAccessibilityData
  const validateAccessibility = !venue.isVirtual && !isAccessibilityDefinedViaAccesLibre

  return (
    <Formik
      initialValues={setInitialFormValues(venue)}
      onSubmit={onSubmit}
      validationSchema={getValidationSchema(validateAccessibility)}
    >
      <Form>
        <ScrollToFirstErrorAfterSubmit />
        <FormLayout fullWidthActions>
          <FormLayout.Section title="Vos informations pour le grand public">
            {validateAccessibility && <MandatoryInfo />}
            <FormLayout.SubSection
              title="À propos de votre activité"
              description={
                venue.isVirtual
                  ? undefined
                  : 'Vous pouvez décrire les différentes actions que vous menez, votre histoire ou préciser des informations sur votre activité.'
              }
            >
              <FormLayout.Row>
                <TextArea
                  name="description"
                  label="Description"
                  description="Par exemple : mon établissement propose des spectacles, de l’improvisation..."
                  maxLength={1000}
                  isOptional
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
            {venue.isPermanent && (
              <FormLayout.SubSection title={isOpenToPublicEnabled ? "Accès et horaires" : "Horaires d'ouverture"}>
                <OpeningHoursForm />
              </FormLayout.SubSection>
            )}
            <AccessibilityForm
              isVenuePermanent={Boolean(venue.isPermanent)}
              externalAccessibilityId={venue.externalAccessibilityId}
              externalAccessibilityData={venue.externalAccessibilityData}
            />
            <FormLayout.SubSection
              title="Contact"
              description="Ces informations permettront aux bénéficiaires de vous contacter en cas de besoin."
            >
              <FormLayout.Row>
                <PhoneNumberInput
                  name="phoneNumber"
                  label="Téléphone"
                  isOptional
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  name="email"
                  label="Adresse email"
                  description="Format : email@exemple.com"
                  isOptional
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  name="webSite"
                  label="URL de votre site web"
                  description="Format : https://exemple.com"
                  isOptional
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
          </FormLayout.Section>
        </FormLayout>

        <FormikConsumer>
          {(formik) => (
            <>
              <VenueFormActionBar
                venue={venue}
                disableFormSubmission={!formik.dirty}
              />
              <RouteLeavingGuardVenueEdition
                shouldBlock={formik.dirty && !formik.isSubmitting}
              />
            </>
          )}
        </FormikConsumer>
      </Form>
    </Formik>
  )
}
