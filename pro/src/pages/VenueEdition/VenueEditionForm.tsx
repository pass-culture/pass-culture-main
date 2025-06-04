import {
  Form,
  FormikConsumer,
  FormikProps,
  FormikProvider,
  useFormik,
} from 'formik'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { isErrorAPIError, serializeApiErrors } from 'apiClient/helpers'
import { GetVenueResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { getFormattedAddress } from 'commons/utils/getFormattedAddress'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MandatoryInfo } from 'components/FormLayout/FormLayoutMandatoryInfo'
import { OpenToPublicToggle } from 'components/OpenToPublicToggle/OpenToPublicToggle'
import { ScrollToFirstErrorAfterSubmit } from 'components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Callout } from 'ui-kit/Callout/Callout'
import { PhoneNumberInput } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'

import { AccessibilityForm } from './AccessibilityForm/AccessibilityForm'
import { getPathToNavigateTo } from './context'
import { OpeningHoursForm } from './OpeningHoursForm/OpeningHoursForm'
import { RouteLeavingGuardVenueEdition } from './RouteLeavingGuardVenueEdition'
import { serializeEditVenueBodyModel } from './serializers'
import { setInitialFormValues } from './setInitialFormValues'
import { VenueEditionFormValues } from './types'
import { getValidationSchema } from './validationSchema'
import styles from './VenueEditionForm.module.scss'
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

  const initialValues = setInitialFormValues(venue)

  const resetOpeningHoursAndAccessibility = async (
    formikProps: FormikProps<VenueEditionFormValues>
  ) => {
    const fieldsToReset: (keyof VenueEditionFormValues)[] = [
      'days',
      'monday',
      'tuesday',
      'wednesday',
      'thursday',
      'friday',
      'saturday',
      'sunday',
      'accessibility',
      'isAccessibilityAppliedOnAllOffers',
    ]

    for (const field of fieldsToReset) {
      await formikProps.setFieldValue(field, initialValues[field])
    }
  }

  const onSubmit = async function (values: VenueEditionFormValues) {
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

      const path = getPathToNavigateTo(venue.managingOfferer.id, venue.id)
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(path)

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
  const isAccessibilityDefinedViaAccesLibre = !!venue.externalAccessibilityData
  const mandatoryFields = {
    isOpenToPublic: isOpenToPublicEnabled,
    // If FF is enabled, acccessibility is mandatory depending on
    // isOpenToPublic value / toggle, which is managed within yup validation schema instead.
    accessibility:
      !isOpenToPublicEnabled &&
      !venue.isVirtual &&
      !isAccessibilityDefinedViaAccesLibre,
  }
  const hasMandatoryInfo =
    mandatoryFields.accessibility || mandatoryFields.isOpenToPublic

  const formik = useFormik({
    initialValues: initialValues,
    onSubmit: onSubmit,
    validationSchema: getValidationSchema({ mandatoryFields }),
  })

  return (
    <FormikProvider value={formik}>
      <Form>
        <ScrollToFirstErrorAfterSubmit />
        <FormLayout fullWidthActions>
          <FormLayout.Section title="Vos informations pour le grand public">
            {hasMandatoryInfo && <MandatoryInfo />}
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
            {isOpenToPublicEnabled ? (
              <FormLayout.SubSection title="Accueil du public">
                <FormLayout.Row>
                  <OpenToPublicToggle
                    onChange={async (e) => {
                      await formik.setFieldValue(
                        'isOpenToPublic',
                        e.target.value
                      )

                      if (e.target.value === 'false') {
                        await resetOpeningHoursAndAccessibility(formik)
                      }
                    }}
                    radioDescriptions={{
                      yes: "Votre adresse postale sera visible, veuillez renseigner vos horaires d'ouvertures et vos modalités d'accessibilité.",
                    }}
                  />
                </FormLayout.Row>
                {formik.values.isOpenToPublic === 'true' && (
                  <>
                    <FormLayout.SubSubSection
                      title="Adresse et horaires"
                      className={styles['opening-hours-subsubsection']}
                    >
                      <FormLayout.Row>
                        <TextInput
                          name="street"
                          label="Adresse postale"
                          className={
                            styles['opening-hours-subsubsection-address-input']
                          }
                          disabled
                          isOptional
                          value={getFormattedAddress(venue.address)}
                        />
                        <Callout
                          testId="address-callout"
                          className={
                            styles['opening-hours-subsubsection-callout']
                          }
                        >
                          Pour modifier l’adresse de votre structure,
                          rendez-vous dans votre page Paramètres généraux.
                        </Callout>
                      </FormLayout.Row>
                      <FormLayout.Row>
                        <OpeningHoursForm />
                      </FormLayout.Row>
                    </FormLayout.SubSubSection>
                    <AccessibilityForm
                      isVenuePermanent={true}
                      externalAccessibilityId={venue.externalAccessibilityId}
                      externalAccessibilityData={
                        venue.externalAccessibilityData
                      }
                      isSubSubSection
                    />
                  </>
                )}
              </FormLayout.SubSection>
            ) : (
              <>
                {venue.isPermanent && (
                  <FormLayout.SubSection title="Horaires d'ouverture">
                    <OpeningHoursForm />
                  </FormLayout.SubSection>
                )}
                <AccessibilityForm
                  isVenuePermanent={Boolean(venue.isPermanent)}
                  externalAccessibilityId={venue.externalAccessibilityId}
                  externalAccessibilityData={venue.externalAccessibilityData}
                />
              </>
            )}
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
                isSubmitting={formik.isSubmitting}
              />
              <RouteLeavingGuardVenueEdition
                shouldBlock={formik.dirty && !formik.isSubmitting}
              />
            </>
          )}
        </FormikConsumer>
      </Form>
    </FormikProvider>
  )
}
