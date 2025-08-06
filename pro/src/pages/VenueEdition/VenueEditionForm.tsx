import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useNotification } from '@/commons/hooks/useNotification'
import { getFormattedAddress } from '@/commons/utils/getFormattedAddress'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { OpenToPublicToggle } from '@/components/OpenToPublicToggle/OpenToPublicToggle'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Callout } from '@/ui-kit/Callout/Callout'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'
import { TextInput } from '@/ui-kit/form/TextInput/TextInput'

import { AccessibilityForm } from './AccessibilityForm/AccessibilityForm'
import { OpeningHoursForm } from './OpeningHoursForm/OpeningHoursForm'
import { RouteLeavingGuardVenueEdition } from './RouteLeavingGuardVenueEdition'
import { serializeEditVenueBodyModel } from './serializers'
import { setInitialFormValues } from './setInitialFormValues'
import { VenueEditionFormValues } from './types'
import styles from './VenueEditionForm.module.scss'
import { VenueFormActionBar } from './VenueFormActionBar/VenueFormActionBar'
import { getValidationSchema } from './validationSchema'

interface VenueFormProps {
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({ venue }: VenueFormProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()

  const initialValues = setInitialFormValues(venue)

  const methods = useForm<VenueEditionFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(getValidationSchema() as any),
    mode: 'onBlur',
  })

  const resetOpeningHoursAndAccessibility = () => {
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
      methods.setValue(field, initialValues[field])
    }
  }

  const onSubmit = async (values: VenueEditionFormValues) => {
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

      const path = getVenuePagePathToNavigateTo(
        venue.managingOfferer.id,
        venue.id
      )
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(path)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: true,
        isEdition: true,
      })

      notify.success('Vos modifications ont été sauvegardées')
    } catch (error) {
      let formErrors: Record<string, string> | undefined
      if (isErrorAPIError(error)) {
        formErrors = error.body
      }

      const errorsKeys = formErrors ? Object.keys(formErrors) : []

      if (
        !formErrors ||
        errorsKeys.length === 0 ||
        errorsKeys.includes('global')
      ) {
        notify.error('Erreur inconnue lors de la sauvegarde de la structure.')
      } else {
        notify.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )

        for (const field of errorsKeys) {
          methods.setError(field as keyof VenueEditionFormValues, {
            type: field,
            message: formErrors[field].toString(),
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
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        <ScrollToFirstHookFormErrorAfterSubmit />
        <FormLayout fullWidthActions>
          <FormLayout.Section title="Vos informations pour le grand public">
            <MandatoryInfo />
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
                  label="Description"
                  description="Par exemple : mon établissement propose des spectacles, de l’improvisation..."
                  maxLength={1000}
                  {...methods.register('description')}
                  error={methods.formState.errors.description?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
            <FormLayout.SubSection title="Accueil du public">
              <FormLayout.Row>
                <OpenToPublicToggle
                  onChange={(e) => {
                    methods.setValue(
                      'isOpenToPublic',
                      e.target.value.toString()
                    )
                    if (e.target.value === 'false') {
                      resetOpeningHoursAndAccessibility()
                    }
                  }}
                  radioDescriptions={{
                    yes: "Votre adresse postale sera visible, veuillez renseigner vos horaires d'ouvertures et vos modalités d'accessibilité.",
                  }}
                  isOpenToPublic={methods.watch('isOpenToPublic')}
                />
              </FormLayout.Row>
              {methods.watch('isOpenToPublic') === 'true' && (
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
                        value={getFormattedAddress(venue.address)}
                      />
                      <Callout
                        testId="address-callout"
                        className={
                          styles['opening-hours-subsubsection-callout']
                        }
                      >
                        Pour modifier l’adresse de votre structure, rendez-vous
                        dans votre page Paramètres généraux.
                      </Callout>
                    </FormLayout.Row>
                    <FormLayout.Row>
                      <OpeningHoursForm />
                    </FormLayout.Row>
                  </FormLayout.SubSubSection>
                  <AccessibilityForm
                    isVenuePermanent={!!venue.isPermanent}
                    externalAccessibilityId={venue.externalAccessibilityId}
                    externalAccessibilityData={venue.externalAccessibilityData}
                    isSubSubSection
                  />
                </>
              )}
            </FormLayout.SubSection>
            <FormLayout.SubSection
              title="Contact"
              description="Ces informations permettront aux bénéficiaires de vous contacter en cas de besoin."
            >
              <FormLayout.Row>
                <PhoneNumberInput
                  {...methods.register('phoneNumber')}
                  label="Téléphone"
                  error={methods.formState.errors.phoneNumber?.message}
                />
              </FormLayout.Row>
              <FormLayout.Row mdSpaceAfter>
                <TextInput
                  label="Adresse email"
                  description="Format : email@exemple.com"
                  {...methods.register('email')}
                  error={methods.formState.errors.email?.message}
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  label="URL de votre site web"
                  description="Format : https://exemple.com"
                  {...methods.register('webSite')}
                  error={methods.formState.errors.webSite?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
          </FormLayout.Section>
        </FormLayout>

        <VenueFormActionBar
          venue={venue}
          isSubmitting={methods.formState.isSubmitting}
        />
        <RouteLeavingGuardVenueEdition
          shouldBlock={
            methods.formState.isDirty && !methods.formState.isSubmitting
          }
        />
      </form>
    </FormProvider>
  )
}
