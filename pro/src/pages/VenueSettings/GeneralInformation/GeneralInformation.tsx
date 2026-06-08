import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation } from 'react-router'

import type { AdresseData } from '@/apiClient/adresse/types'
import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1/new'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ActivityNotOpenToPublicMap } from '@/commons/mappings/ActivityNotOpenToPublic'
import { ActivityOpenToPublicMap } from '@/commons/mappings/ActivityOpenToPublic'
import { getMapKeys } from '@/commons/mappings/helpers'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { AddressFields } from '@/components/AddressFields/AddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { OpenToPublicToggle } from '@/components/OpenToPublicToggle/OpenToPublicToggle'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { ReimbursementFields } from '@/pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
import { ActivityDetails } from '@/pages/VenueEdition/components/ActivityDetails/ActivityDetails'
import { RouteLeavingGuardVenueEdition } from '@/pages/VenueEdition/components/RouteLeavingGuardVenueEdition'
import { VenueFormActionBar } from '@/pages/VenueEdition/components/VenueFormActionBar/VenueFormActionBar'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'

import { useSaveVenueSettings } from '../commons/hooks/useSaveVenueSettings'
import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../commons/types'
import { toFormValues } from '../commons/utils/toFormValues'
import { venueSettingsValidationSchema } from '../commons/validationSchema'
import { SiretOrCommentFields } from '../components/SiretOrCommentFields/SiretOrCommentFields'

const GeneralInformation = () => {
  const venue = useAppSelector(ensureSelectedPartnerVenue)

  const formContext: VenueSettingsFormContext = {
    isCaledonian: venue.isCaledonian,
    siren: venue.managingOfferer?.siren,
    withSiret: Boolean(venue.siret),
    isOpenToPublic: venue.isOpenToPublic.toString(),
    activity: venue.activity as VenueSettingsFormValues['activity'],
  }

  const initialValues: VenueSettingsFormValues = toFormValues({ venue })

  const form = useForm<VenueSettingsFormValues>({
    context: formContext,
    defaultValues: initialValues,
    resolver: yupResolver(
      // biome-ignore lint/suspicious/noExplicitAny: TODO : review validation schema
      venueSettingsValidationSchema as any
    ),
    mode: 'onBlur',
  })

  const { saveAndContinue } = useSaveVenueSettings({ form, venue })

  const onSubmit = (formValues: VenueSettingsFormValues) =>
    saveAndContinue(formValues, formContext)

  const {
    register,
    setValue,
    watch,
    clearErrors,
    formState: { isDirty, isSubmitting, isSubmitted, errors, disabled },
  } = form

  const location = useLocation()
  const manuallySetAddress = watch('manuallySetAddress')

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)
    resetReactHookFormAddressFields<VenueSettingsFormValues>(
      (name, defaultValue) => setValue(name, defaultValue)
    )
    clearErrors()
  }

  const onAddressSelect = (data: AdresseData) => {
    setValue('street', data.address)
    setValue('postalCode', data.postalCode)
    setValue('city', data.city)
    setValue('latitude', data.latitude.toString())
    setValue('longitude', data.longitude.toString())
    setValue('banId', data.id)
    setValue('inseeCode', data.inseeCode)
    setValue('coords', `${data.latitude}, ${data.longitude}`)
  }

  const resetOpeningHoursAndAccessibility = () => {
    const fieldsToReset: (keyof VenueSettingsFormValues)[] = [
      'accessibility',
      'isAccessibilityAppliedOnAllOffers',
    ]

    for (const field of fieldsToReset) {
      form.setValue(field, initialValues[field])
    }
  }

  const toggleOpenToPublic = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isOpenToPublicValue = e.target.value.toString()

    form.setValue('isOpenToPublic', isOpenToPublicValue, { shouldDirty: true })

    if (isOpenToPublicValue === 'false') {
      resetOpeningHoursAndAccessibility()
    }

    const isInitialActivityValid =
      formContext.activity != null &&
      (isOpenToPublicValue === 'true'
        ? getMapKeys(ActivityOpenToPublicMap).includes(
            formContext.activity as ActivityOpenToPublic
          )
        : getMapKeys(ActivityNotOpenToPublicMap).includes(
            formContext.activity as ActivityNotOpenToPublic
          ))

    if (isInitialActivityValid) {
      form.setValue('activity', formContext.activity)
      form.clearErrors('activity')
    } else {
      form.setValue('activity', null)
    }
  }

  return (
    <>
      <MandatoryInfo />
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
          <ScrollToFirstHookFormErrorAfterSubmit />
          <FormLayout fullWidthActions>
            <FormLayout.Section title="Informations administratives">
              <FormLayout.Row>
                <SiretOrCommentFields formContext={formContext} />
              </FormLayout.Row>

              <FormLayout.Row mdSpaceAfter>
                <TextInput
                  label="Raison sociale"
                  {...register('name')}
                  disabled
                  error={errors.name?.message}
                />
              </FormLayout.Row>

              <FormLayout.Row>
                <TextInput
                  {...register('publicName')}
                  label="Nom public"
                  description="À remplir si différent de la raison sociale. En le remplissant, c'est ce dernier qui sera visible du public."
                />
              </FormLayout.Row>
            </FormLayout.Section>

            <FormLayout.SubSection title="Accueil du public">
              <FormLayout.Row mdSpaceAfter>
                <OpenToPublicToggle
                  onChange={toggleOpenToPublic}
                  isOpenToPublic={form.watch('isOpenToPublic')}
                />
              </FormLayout.Row>
              {form.watch('isOpenToPublic') === 'true' && (
                <AddressFields
                  description="Indiquez ici l'adresse où vous recevez votre public."
                  addressRegister={register('addressAutocomplete')}
                  disabled={disabled}
                  onAddressChosen={onAddressSelect}
                  error={errors.addressAutocomplete?.message}
                  renderManual={() => <AddressManual />}
                  manual={manuallySetAddress}
                  onManualChange={toggleManuallySetAddress}
                />
              )}
            </FormLayout.SubSection>
            <FormLayout.SubSection title="À propos de votre activité">
              <ActivityDetails />
            </FormLayout.SubSection>

            {venue.pricingPoint?.id && (
              <ReimbursementFields
                scrollToSection={
                  Boolean(location.state) || Boolean(location.hash)
                }
                venuePricingPoint={venue.pricingPoint}
              />
            )}
          </FormLayout>
          <VenueFormActionBar isSubmitting={isSubmitting} isSettingsPage />
          <RouteLeavingGuardVenueEdition
            shouldBlock={isDirty && !isSubmitting && !isSubmitted}
          />
        </form>
      </FormProvider>
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = GeneralInformation
