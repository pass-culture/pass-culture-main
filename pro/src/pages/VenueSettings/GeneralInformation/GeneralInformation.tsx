import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation } from 'react-router'

import type { AdresseData } from '@/apiClient/adresse/types'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { AddressFields } from '@/components/AddressFields/AddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { ReimbursementFields } from '@/pages/Offerers/Offerer/VenueV1/fields/ReimbursementFields/ReimbursementFields'
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
import { WithdrawalDetails } from '../components/WithdrawalDetails/WithdrawalDetails'

const GeneralInformation = () => {
  const venue = useAppSelector(ensureSelectedPartnerVenue)

  const formContext: VenueSettingsFormContext = {
    isCaledonian: venue.isCaledonian,
    isVenueVirtual: venue.isVirtual ?? false,
    siren: venue.managingOfferer?.siren,
    withSiret: Boolean(venue.siret),
  }

  const form = useForm<VenueSettingsFormValues>({
    context: formContext,
    defaultValues: toFormValues({ venue }),
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

  return (
    <>
      <MandatoryInfo />
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
          <ScrollToFirstHookFormErrorAfterSubmit />
          <FormLayout fullWidthActions>
            <FormLayout.Section title="Informations administratives">
              {!venue.isVirtual && (
                <FormLayout.Row>
                  <SiretOrCommentFields formContext={formContext} />
                </FormLayout.Row>
              )}

              <FormLayout.Row mdSpaceAfter>
                <TextInput
                  label="Raison sociale"
                  {...register('name')}
                  disabled
                  error={errors.name?.message}
                />
              </FormLayout.Row>

              {!venue.isVirtual && (
                <>
                  <FormLayout.Row mdSpaceAfter>
                    <TextInput
                      {...register('publicName')}
                      label="Nom public"
                      description="À remplir si différent de la raison sociale. En le remplissant, c'est ce dernier qui sera visible du public."
                    />
                  </FormLayout.Row>

                  <AddressFields
                    addressRegister={register('addressAutocomplete')}
                    disabled={disabled}
                    onAddressChosen={onAddressSelect}
                    error={errors.addressAutocomplete?.message}
                    renderManual={() => <AddressManual />}
                    manual={manuallySetAddress}
                    onManualChange={toggleManuallySetAddress}
                  />
                </>
              )}
            </FormLayout.Section>

            {!venue.isVirtual && <WithdrawalDetails />}

            {venue.pricingPoint?.id && (
              <ReimbursementFields
                scrollToSection={
                  Boolean(location.state) || Boolean(location.hash)
                }
                venuePricingPoint={venue.pricingPoint}
              />
            )}
          </FormLayout>
          <VenueFormActionBar isSubmitting={isSubmitting} />
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
