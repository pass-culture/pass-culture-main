import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { getActivities } from '@/commons/mappings/mappings'
import { getFormattedAddress } from '@/commons/utils/getFormattedAddress'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { objectKeys } from '@/commons/utils/object'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { OpeningHours } from '@/components/OpeningHours/OpeningHours'
import { OpenToPublicToggle } from '@/components/OpenToPublicToggle/OpenToPublicToggle'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { ActivityDetails } from '@/pages/VenueEdition/components/ActivityDetails/ActivityDetails'
import { WithdrawalDetails } from '@/pages/VenueSettings/components/WithdrawalDetails/WithdrawalDetails'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'

import { getVolunteeringUrlError } from '../commons/getVolunteeringUrlError'
import { serializeEditVenueBodyModel } from '../commons/serializers'
import { setInitialFormValues } from '../commons/setInitialFormValues'
import type { VenueEditionFormValues } from '../commons/types'
import { getValidationSchema } from '../commons/validationSchema'
import { AccessibilityForm } from './AccessibilityForm/AccessibilityForm'
import { RouteLeavingGuardVenueEdition } from './RouteLeavingGuardVenueEdition'
import styles from './VenueEditionForm.module.scss'
import { VenueFormActionBar } from './VenueFormActionBar/VenueFormActionBar'

interface VenueFormProps {
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({ venue }: VenueFormProps) => {
  const { syncVenueWithData } = useSyncVenueCache()
  const isVolunteeringActive = useActiveFeature('WIP_VOLUNTEERING')

  const navigate = useNavigate()
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const initialValues: VenueEditionFormValues = setInitialFormValues(venue)

  const methods = useForm<VenueEditionFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(getValidationSchema()),
    mode: 'onBlur',
  })

  const resetOpeningHoursAndAccessibility = () => {
    const fieldsToReset: (keyof VenueEditionFormValues)[] = [
      'accessibility',
      'isAccessibilityAppliedOnAllOffers',
    ]

    for (const field of fieldsToReset) {
      methods.setValue(field, initialValues[field])
    }
  }

  const onSubmit = async (values: VenueEditionFormValues) => {
    try {
      const updatedVenue = await api.editVenue(
        venue.id,
        serializeEditVenueBodyModel(
          values,
          !venue.siret,
          venue.openingHours !== null
        )
      )

      await syncVenueWithData(venue.id, updatedVenue)

      const path = getVenuePagePathToNavigateTo()
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(path)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: true,
        isEdition: true,
      })

      snackBar.success('Vos modifications ont été sauvegardées')
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
        snackBar.error('Erreur inconnue lors de la sauvegarde de la structure.')
      } else {
        snackBar.error(
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
        saved: false,
        isEdition: true,
      })
    }
  }

  const toggleOpenToPublic = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isOpenToPublicValue = e.target.value.toString()

    methods.setValue('isOpenToPublic', isOpenToPublicValue, {
      shouldDirty: true,
    })

    if (isOpenToPublicValue === 'false') {
      resetOpeningHoursAndAccessibility()
    }

    const activityKeys = objectKeys(
      getActivities(
        isOpenToPublicValue === 'true' ? 'OPEN_TO_PUBLIC' : 'NOT_OPEN_TO_PUBLIC'
      )
    )
    const isInitialActivityValid = initialValues.activity
      ? activityKeys.includes(initialValues.activity)
      : false

    if (isInitialActivityValid) {
      methods.setValue('activity', initialValues.activity)
      methods.clearErrors('activity')
    } else {
      methods.setValue('activity', null)
    }
  }

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        <ScrollToFirstHookFormErrorAfterSubmit />
        <FormLayout fullWidthActions>
          <FormLayout.Section title="Vos informations">
            <MandatoryInfo />
            {isVolunteeringActive && (
              <FormLayout.SubSection
                title="Bénévolat"
                isNew
                description={
                  <>
                    Proposez des missions de bénévolat au sein du service{' '}
                    <span className={styles['volunteering-link']}>
                      <Button
                        as="a"
                        variant={ButtonVariant.TERTIARY}
                        isExternal
                        opensInNewTab
                        to="https://www.jeveuxaider.gouv.fr/"
                        color={ButtonColor.NEUTRAL}
                        size={ButtonSize.SMALL}
                        label={'JeVeuxAider.gouv.fr'}
                      />
                    </span>{' '}
                    et permettez aux jeunes de s’engager à vos côtés.
                  </>
                }
              >
                <FormLayout.Row>
                  <TextInput
                    {...methods.register('volunteeringUrl')}
                    name="volunteeringUrl"
                    label="URL de votre page JeVeuxAider.gouv.fr"
                    description="Format : https://www.jeveuxaider.gouv.fr/organisations/exemple"
                    error={methods.formState.errors.volunteeringUrl?.message}
                    onBlur={(event) => {
                      const value = event.target.value
                      const error = getVolunteeringUrlError(value)
                      if (value.trim() && error) {
                        methods.setError('volunteeringUrl', {
                          type: 'manual',
                          message: error,
                        })
                        logEvent(Events.VENUE_FORM_VOLUNTEERING_URL_ERROR, {
                          volunteeringUrl: value,
                        })
                      }
                    }}
                  />
                </FormLayout.Row>
              </FormLayout.SubSection>
            )}

            <FormLayout.SubSection title="Accueil du public">
              <FormLayout.Row>
                <OpenToPublicToggle
                  onChange={toggleOpenToPublic}
                  radioDescriptions={{
                    yes: 'Votre adresse postale sera visible',
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
                      <div
                        className={
                          styles['opening-hours-subsubsection-address-input']
                        }
                      >
                        <TextInput
                          name="street"
                          label="Adresse postale"
                          disabled
                          value={getFormattedAddress(venue.location)}
                        />
                      </div>
                      <div
                        data-testid="address-callout"
                        className={
                          styles['opening-hours-subsubsection-callout']
                        }
                      >
                        <Banner
                          title="Modification dans Paramètres"
                          description="L'adresse de votre structure se modifie dans la page Paramètres."
                        />
                      </div>
                    </FormLayout.Row>
                    <FormLayout.Row>
                      <fieldset>
                        <legend>Horaires d’ouverture</legend>
                        <div className={styles['opening-hours']}>
                          <OpeningHours />
                        </div>
                      </fieldset>
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

            <ActivityDetails isVenueVirtual={!!venue.isVirtual} />

            {!venue.isVirtual && <WithdrawalDetails />}

            <FormLayout.SubSection
              title="Informations de contact"
              description="Ces informations permettront aux bénéficiaires de vous contacter en cas de besoin."
            >
              <FormLayout.Row mdSpaceAfter>
                <PhoneNumberInput
                  {...methods.register('phoneNumber')}
                  label="Téléphone"
                  error={methods.formState.errors.phoneNumber?.message}
                />
              </FormLayout.Row>
              <FormLayout.Row mdSpaceAfter>
                <TextInput
                  label="Adresse email"
                  type="email"
                  description="Format : email@exemple.com"
                  {...methods.register('email')}
                  error={methods.formState.errors.email?.message}
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  label="URL de votre site web"
                  type="url"
                  description="Format : https://exemple.com"
                  maxLength={256}
                  {...methods.register('webSite')}
                  error={methods.formState.errors.webSite?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
          </FormLayout.Section>
        </FormLayout>

        <VenueFormActionBar isSubmitting={methods.formState.isSubmitting} />
        <RouteLeavingGuardVenueEdition
          shouldBlock={
            methods.formState.isDirty && !methods.formState.isSubmitting
          }
        />
      </form>
    </FormProvider>
  )
}
