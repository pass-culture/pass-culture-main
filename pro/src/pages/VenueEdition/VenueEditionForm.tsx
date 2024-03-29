import { Form, Formik, FormikConfig, FormikConsumer } from 'formik'
import { useNavigate, useLocation } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetVenueResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { Events } from 'core/FirebaseEvents/constants'
import { PATCH_SUCCESS_MESSAGE } from 'core/shared'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { TextArea, TextInput } from 'ui-kit'
import PhoneNumberInput from 'ui-kit/form/PhoneNumberInput'

import { Accessibility } from '../VenueCreation/Accessibility/Accessibility'
import { VenueFormActionBar } from '../VenueCreation/VenueFormActionBar/VenueFormActionBar'

import { OpeningHoursForm } from './OpeningHoursForm/OpeningHoursForm'
import { RouteLeavingGuardVenueEdition } from './RouteLeavingGuardVenueEdition'
import { serializeEditVenueBodyModel } from './serializers'
import { setInitialFormValues } from './setInitialFormValues'
import { VenueEditionFormValues } from './types'
import { getValidationSchema } from './validationSchema'
import { GET_VENUE_QUERY_KEY } from './VenueEdition'

interface VenueFormProps {
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({ venue }: VenueFormProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const isOpeningHoursEnabled = useActiveFeature('WIP_OPENING_HOURS')

  const { currentUser } = useCurrentUser()

  const onSubmit: FormikConfig<VenueEditionFormValues>['onSubmit'] = async (
    values,
    formikHelpers
  ) => {
    try {
      await api.editVenue(
        venue.id,
        serializeEditVenueBodyModel(values, !venue.siret, isOpeningHoursEnabled)
      )

      await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])

      navigate(`/structures/${venue.managingOfferer.id}/lieux/${venue.id}`)

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
        formikHelpers.setErrors(serializeApiErrors(formErrors, apiFieldsMap))
        formikHelpers.setStatus('apiError')
      }

      logEvent?.(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: false,
        isEdition: true,
      })
    }
  }

  return (
    <Formik
      initialValues={setInitialFormValues(venue)}
      onSubmit={onSubmit}
      validationSchema={getValidationSchema(venue.isVirtual)}
    >
      <Form>
        <FormLayout fullWidthActions>
          <FormLayout.Section title="Vos informations pour le grand public">
            <FormLayout.SubSection
              title="À propos de votre activité"
              description={
                venue.isVirtual
                  ? undefined
                  : 'Cet espace vous permet de présenter votre activité culturelle aux utilisateurs de l’application pass Culture. Vous pouvez décrire les différentes actions que vous menez, votre histoire ou préciser des informations sur votre activité.'
              }
            >
              <FormLayout.Row>
                <TextArea
                  name="description"
                  label="Description"
                  placeholder="Par exemple : mon établissement propose des spectacles, de l’improvisation..."
                  maxLength={1000}
                  countCharacters
                  isOptional
                />
              </FormLayout.Row>
            </FormLayout.SubSection>

            <Accessibility isCreatingVenue={false} />

            {isOpeningHoursEnabled && venue.isPermanent && (
              <FormLayout.SubSection title="Horaires d'ouverture">
                <OpeningHoursForm />
              </FormLayout.SubSection>
            )}

            <FormLayout.SubSection
              title="Contact"
              description={
                'Ces informations seront affichées dans votre page partenaire, sur l’application pass Culture. ' +
                'Elles permettront aux bénéficiaires de vous contacter en cas de besoin.'
              }
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
                  placeholder="email@exemple.com"
                  isOptional
                />
              </FormLayout.Row>

              <FormLayout.Row>
                <TextInput
                  name="webSite"
                  label="URL de votre site web"
                  placeholder="https://exemple.com"
                  isOptional
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
          </FormLayout.Section>
        </FormLayout>

        <VenueFormActionBar venue={venue} />

        <FormikConsumer>
          {(formik) => (
            <RouteLeavingGuardVenueEdition
              shouldBlock={formik.dirty && !formik.isSubmitting}
            />
          )}
        </FormikConsumer>
      </Form>
    </Formik>
  )
}
