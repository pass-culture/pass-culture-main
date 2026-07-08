import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { getVolunteeringUrlError } from '@/commons/core/VenueEdition/getVolunteeringUrlError'
import { serializeEditVenueBodyModel } from '@/commons/core/VenueEdition/serializeEditVenueBodyModel'
import { setInitialFormValues } from '@/commons/core/VenueEdition/setInitialFormValues'
import type { VenueEditionFormValues } from '@/commons/core/VenueEdition/types'
import { getValidationSchema } from '@/commons/core/VenueEdition/validationSchema'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { getFormattedAddress } from '@/commons/utils/getFormattedAddress'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { OpeningHours } from '@/components/VenueEdition/OpeningHours/OpeningHours'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullInfoIcon from '@/icons/full-info.svg'
import fullNextIcon from '@/icons/full-next.svg'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

import { AccessibilityForm } from '../../../components/VenueEdition/AccessibilityForm/AccessibilityForm'
import { ActivityDetailsReadOnly } from '../../../components/VenueEdition/ActivityDetails/ActivityDetailsReadOnly/ActivityDetailsReadOnly'
import { VenueFormActionBar } from '../../../components/VenueEdition/VenueFormActionBar/VenueFormActionBar'
import styles from './VenueEditionForm.module.scss'
import { WithdrawalDetails } from './WithdrawalDetails/WithdrawalDetails'

interface VenueFormProps {
  venue: GetVenueResponseModel
}

export const VenueEditionForm = ({ venue }: VenueFormProps) => {
  const { syncVenueWithData } = useSyncVenueCache()

  const navigate = useNavigate()
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const initialValues: VenueEditionFormValues = setInitialFormValues(venue)

  const form = useForm<VenueEditionFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(getValidationSchema()),
    mode: 'onBlur',
  })

  const onCancel = () => {
    form.reset()
    navigate(getVenuePagePathToNavigateTo())
  }

  const onSubmit = async (values: VenueEditionFormValues): Promise<boolean> => {
    try {
      const updatedVenue = await api.editVenue({
        path: { venue_id: venue.id },
        body: serializeEditVenueBodyModel(
          values,
          !venue.siret,
          venue.openingHours !== null
        ),
      })

      await syncVenueWithData(venue.id, updatedVenue)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: true,
        isEdition: true,
      })

      snackBar.success('Vos modifications ont été sauvegardées')

      return true
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
          form.setError(field as keyof VenueEditionFormValues, {
            type: field,
            message: formErrors[field].toString(),
          })
        }
      }

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: false,
        isEdition: true,
      })

      return false
    }
  }

  const { navigationGuardDialog, navigationGuardedSubmitHandler } =
    useFormNavigationGuard({
      afterSubmitPath: getVenuePagePathToNavigateTo(),
      form,
      onSubmit,
    })

  return (
    <FormProvider {...form}>
      <form onSubmit={navigationGuardedSubmitHandler}>
        <ScrollToFirstHookFormErrorAfterSubmit />
        <FormLayout fullWidthActions>
          <FormLayout.Section
            title={
              venue.isOpenToPublic
                ? 'Vos informations pour le grand public'
                : 'Vos informations'
            }
          >
            <FormLayout.SubSection
              title="À propos de votre activité"
              className={styles['sub-section--first']}
            >
              <FormLayout.Row mdSpaceAfter>
                <ActivityDetailsReadOnly
                  venue={venue}
                  isEditionMode
                ></ActivityDetailsReadOnly>
              </FormLayout.Row>
              <FormLayout.Row mdSpaceAfter>
                <Banner
                  title="Les informations liées à votre activité se modifient dans la page Paramètres."
                  variant={BannerVariants.DEFAULT}
                  icon={fullInfoIcon}
                  actions={[
                    {
                      label: 'Accéder à la page Paramètres',
                      icon: fullNextIcon,
                      href: '/parametres',
                      type: 'link',
                    },
                  ]}
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextArea
                  {...form.register('description')}
                  label="Description"
                  maxLength={1000}
                  description={
                    'Vous pouvez décrire les différentes actions que vous menez, votre histoire ou préciser des informations sur votre activité.'
                  }
                  error={form.formState.errors.description?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
            {venue.isOpenToPublic && (
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
                      {`Adresse : ${getFormattedAddress(venue.location)}`}
                    </div>
                    <div data-testid="address-callout">
                      <Banner
                        title="L'adresse de votre structure se modifie dans la page Paramètres."
                        actions={[
                          {
                            label: 'Accéder à la page Paramètres',
                            icon: fullNextIcon,
                            href: '/parametres',
                            type: 'link',
                          },
                        ]}
                      />
                    </div>
                  </FormLayout.Row>
                  <FormLayout.Row>
                    <fieldset>
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
            <WithdrawalDetails />
            <FormLayout.SubSection
              title="Bénévolat"
              className={styles['sub-section']}
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
                  {...form.register('volunteeringUrl')}
                  name="volunteeringUrl"
                  label="URL de votre page JeVeuxAider.gouv.fr"
                  description="Format : https://www.jeveuxaider.gouv.fr/organisations/exemple"
                  error={form.formState.errors.volunteeringUrl?.message}
                  onBlur={(event) => {
                    const value = event.target.value
                    const error = getVolunteeringUrlError(value)
                    if (value.trim() && error) {
                      form.setError('volunteeringUrl', {
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
            <FormLayout.SubSection
              title="Informations de contact"
              description="Ces informations permettront aux bénéficiaires de vous contacter en cas de besoin."
              className={styles['sub-section']}
            >
              <FormLayout.Row mdSpaceAfter>
                <PhoneNumberInput
                  {...form.register('phoneNumber')}
                  label="Téléphone"
                  error={form.formState.errors.phoneNumber?.message}
                />
              </FormLayout.Row>
              <FormLayout.Row mdSpaceAfter>
                <TextInput
                  label="Adresse email"
                  type="email"
                  description="Format : email@exemple.com"
                  autoComplete="email"
                  {...form.register('email')}
                  error={form.formState.errors.email?.message}
                />
              </FormLayout.Row>
              <FormLayout.Row>
                <TextInput
                  label="URL de votre site web"
                  type="url"
                  description="Format : https://exemple.com"
                  maxLength={256}
                  {...form.register('webSite')}
                  error={form.formState.errors.webSite?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>
          </FormLayout.Section>
        </FormLayout>

        <VenueFormActionBar
          isSubmitting={form.formState.isSubmitting}
          onCancel={onCancel}
        />
      </form>

      {navigationGuardDialog}
    </FormProvider>
  )
}
