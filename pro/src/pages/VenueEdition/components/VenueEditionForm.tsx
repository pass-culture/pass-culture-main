import { yupResolver } from '@hookform/resolvers/yup'
import { useMemo } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useEducationalDomains } from '@/commons/hooks/swr/useEducationalDomains'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { getActivities } from '@/commons/mappings/mappings'
import { setSelectedVenue } from '@/commons/store/user/reducer'
import { buildSelectOptions } from '@/commons/utils/buildSelectOptions'
import { getFormattedAddress } from '@/commons/utils/getFormattedAddress'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import { objectKeys } from '@/commons/utils/object'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { OpeningHours } from '@/components/OpeningHours/OpeningHours'
import { OpenToPublicToggle } from '@/components/OpenToPublicToggle/OpenToPublicToggle'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { Banner } from '@/design-system/Banner/Banner'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { MultiSelect, type Option } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { PhoneNumberInput } from '@/ui-kit/form/PhoneNumberInput/PhoneNumberInput'
import { Select } from '@/ui-kit/form/Select/Select'
import { TextArea } from '@/ui-kit/form/TextArea/TextArea'

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
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const navigate = useNavigate()
  const location = useLocation()
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const { mutate } = useSWRConfig()
  const { data: educationalDomains, isLoading: isLoadingEducationalDomains } =
    useEducationalDomains()

  const dispatch = useAppDispatch()

  const initialValues: VenueEditionFormValues = setInitialFormValues(venue)

  const methods = useForm<VenueEditionFormValues>({
    defaultValues: initialValues,
    resolver: yupResolver(getValidationSchema()),
    mode: 'onBlur',
  })

  const defaultCulturalDomain: Option[] | undefined = useMemo(() => {
    return educationalDomains.length === 0 ||
      !methods.formState.defaultValues ||
      !methods.formState.defaultValues?.culturalDomains
      ? undefined
      : educationalDomains
          .filter((apiDomain) =>
            methods.formState.defaultValues?.culturalDomains?.find(
              (domain) => apiDomain.name === domain
            )
          )
          .map((domain) => {
            return { id: String(domain.id), label: domain.name }
          })
  }, [educationalDomains, methods.formState.defaultValues])

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

      if (withSwitchVenueFeature) {
        dispatch(setSelectedVenue(updatedVenue))
      } else {
        await mutate([GET_VENUE_QUERY_KEY, String(venue.id)])
      }

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
        from: location.pathname,
        saved: false,
        isEdition: true,
      })
    }
  }

  const onOpenToPublicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isOpenToPublicValue = e.target.value.toString()

    methods.setValue('isOpenToPublic', isOpenToPublicValue)

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

            <FormLayout.SubSection title="Accueil du public">
              <FormLayout.Row>
                <OpenToPublicToggle
                  onChange={onOpenToPublicChange}
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
                          description="L'adresse de votre structure se modifie dans la page Paramètres généraux."
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

            <FormLayout.SubSection title="À propos de votre activité">
              <FormLayout.Row key={methods.watch('activity')} mdSpaceAfter>
                <Select
                  {...methods.register('activity')}
                  options={[
                    ...(methods.watch('activity') === null // `activity` may be null if the venue wasn't yet open to public. In that case, we provide a default value so the field isn't rendered "blank"
                      ? [
                          {
                            value: '',
                            label: 'Sélectionnez votre activité principale',
                          },
                        ]
                      : []),
                    ...buildSelectOptions(
                      getActivities(
                        methods.watch('isOpenToPublic') === 'true'
                          ? 'OPEN_TO_PUBLIC'
                          : 'NOT_OPEN_TO_PUBLIC'
                      )
                    ),
                  ]}
                  label="Activité principale"
                  disabled={venue.isVirtual}
                  error={methods.formState.errors.activity?.message}
                  required
                />
              </FormLayout.Row>
              {!isLoadingEducationalDomains && (
                <FormLayout.Row mdSpaceAfter>
                  <MultiSelect
                    name="culturalDomains"
                    options={educationalDomains.map((educationalDomain) => ({
                      id: String(educationalDomain.id),
                      label: educationalDomain.name,
                    }))}
                    defaultOptions={defaultCulturalDomain}
                    error={methods.formState.errors.culturalDomains?.message}
                    label="Domaine(s) d’activité"
                    className={styles['cultural-domains-select']}
                    required={methods.watch('isOpenToPublic') === 'false'}
                    onSelectedOptionsChanged={(selectedOptions) => {
                      methods.setValue(
                        'culturalDomains',
                        selectedOptions.map((opt) => opt.label)
                      )
                    }}
                    buttonLabel={
                      (methods.watch('culturalDomains') ?? []).length > 0
                        ? pluralizeFr(
                            (methods.watch('culturalDomains') ?? []).length,
                            'domaine sélectionné',
                            'domaines sélectionnés'
                          )
                        : 'Sélectionnez un ou plusieurs domaines d’activité'
                    }
                  />
                </FormLayout.Row>
              )}

              <FormLayout.Row>
                {!venue.isVirtual && (
                  <p className={styles['description-helper']}>
                    Vous pouvez décrire les différentes actions que vous menez,
                    votre histoire ou préciser des informations sur votre
                    activité.
                  </p>
                )}
                <TextArea
                  label="Description"
                  description="Par exemple : mon établissement propose des spectacles, de l’improvisation..."
                  maxLength={1000}
                  {...methods.register('description')}
                  error={methods.formState.errors.description?.message}
                />
              </FormLayout.Row>
            </FormLayout.SubSection>

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
