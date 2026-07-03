import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation } from 'react-router'

import type { AdresseData } from '@/apiClient/adresse/types'
import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useKey } from '@/commons/hooks/useKey'
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
import { ActivityDetails } from '@/components/VenueEdition/ActivityDetails/ActivityDetails'
import { VenueFormActionBar } from '@/components/VenueEdition/VenueFormActionBar/VenueFormActionBar'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'

import { scrollToTop } from '../../../commons/utils/scrollToTop'
import { useSaveVenueSettings } from './commons/hooks/useSaveVenueSettings'
import { venueSettingsValidationSchema } from './commons/schema'
import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from './commons/types'
import { toFormValues } from './commons/utils/toFormValues'
import { AddressChangeDialog } from './components/AddressChangeDialog/AddressChangeDialog'
import { ComplementaryInfosDrawer } from './components/ComplementaryInfosDrawer/ComplementaryInfosDrawer'
import { ReimbursementFields } from './components/ReimbursementFields/ReimbursementFields'
import { SiretOrCommentFields } from './components/SiretOrCommentFields/SiretOrCommentFields'

const GeneralInformation = () => {
  const venue = useAppSelector(ensureSelectedPartnerVenue)
  const addressFieldKey = useKey()

  const formContext: VenueSettingsFormContext = {
    isCaledonian: venue.isCaledonian,
    siren: venue.managingOfferer?.siren,
    withSiret: Boolean(venue.siret),
    siret: venue.siret,
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

  const { save: saveAndContinue } = useSaveVenueSettings({ form, venue })
  const [isAddressChangeDialogOpen, setIsAddressChangeDialogOpen] =
    useState(false)
  const [isComplementaryInfosDrawerOpen, setIsComplementaryInfosDrawerOpen] =
    useState(false)
  const [hasAddressChanged, setHasAddressChanged] = useState(false)

  const onCancel = () => {
    form.reset()
    scrollToTop()
  }

  const onSubmit = async (
    formValues: VenueSettingsFormValues
  ): Promise<boolean> => {
    const canProceed = await saveAndContinue(formValues, formContext)

    const hasAddressChanged =
      formValues.addressAutocomplete !== initialValues.addressAutocomplete
    const shouldShowAddressChangeWarning =
      formValues.isOpenToPublic === 'true' &&
      initialValues.isOpenToPublic === 'true' &&
      venue.hasActiveIndividualOffer &&
      hasAddressChanged
    const hasBecomeOpenToPublic =
      formValues.isOpenToPublic === 'true' &&
      initialValues.isOpenToPublic === 'false' &&
      venue.hasActiveIndividualOffer
    const hasSiretChanged =
      formValues.isOpenToPublic === 'true' &&
      formValues.siret !== initialValues.siret

    if (canProceed) {
      setHasAddressChanged(hasAddressChanged)
      if (shouldShowAddressChangeWarning && !hasSiretChanged) {
        setIsAddressChangeDialogOpen(true)
      }
      if (hasBecomeOpenToPublic || hasSiretChanged) {
        setIsComplementaryInfosDrawerOpen(true)
      }
    }

    scrollToTop()

    return canProceed
  }

  const {
    register,
    setValue,
    watch,
    getValues,
    clearErrors,
    formState: { isSubmitting, errors, disabled },
  } = form

  const { navigationGuardDialog, navigationGuardedSubmitHandler } =
    useFormNavigationGuard({ form, onSubmit })

  const location = useLocation()
  const manuallySetAddress = watch('manuallySetAddress')
  const isOpenToPublic = watch('isOpenToPublic')

  const toggleManuallySetAddress = () => {
    setValue('manuallySetAddress', !manuallySetAddress)
    resetReactHookFormAddressFields<VenueSettingsFormValues>(setValue)
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

  const toggleOpenToPublic = (e: React.ChangeEvent<HTMLInputElement>) => {
    const isOpenToPublicValue = e.target.value.toString()
    const currentAddressAutocomplete = getValues('addressAutocomplete')

    form.setValue('isOpenToPublic', isOpenToPublicValue, { shouldDirty: true })

    if (isOpenToPublicValue === 'false') {
      if (!currentAddressAutocomplete && initialValues.addressAutocomplete) {
        resetReactHookFormAddressFields<VenueSettingsFormValues>((name) =>
          // @ts-expect-error Hard to reconcile types with the current complexity.
          setValue(name, initialValues[name])
        )
      }
      form.setValue('accessibility', initialValues.accessibility)
      form.setValue(
        'isAccessibilityAppliedOnAllOffers',
        initialValues.isAccessibilityAppliedOnAllOffers
      )
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
        <form onSubmit={navigationGuardedSubmitHandler} noValidate>
          <ScrollToFirstHookFormErrorAfterSubmit />
          <FormLayout fullWidthActions>
            <FormLayout.Section title="Informations administratives">
              <FormLayout.Row>
                <SiretOrCommentFields
                  formContext={formContext}
                  onAddressUpdate={addressFieldKey.update}
                />
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
                  isOpenToPublic={isOpenToPublic}
                />
              </FormLayout.Row>
              {isOpenToPublic === 'true' && (
                <AddressFields
                  key={addressFieldKey.value}
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
          <VenueFormActionBar isSubmitting={isSubmitting} onCancel={onCancel} />
        </form>
      </FormProvider>

      <AddressChangeDialog
        open={isAddressChangeDialogOpen}
        onOpenChange={setIsAddressChangeDialogOpen}
      />

      <ComplementaryInfosDrawer
        open={isComplementaryInfosDrawerOpen}
        onOpenChange={setIsComplementaryInfosDrawerOpen}
        hasAddressChanged={hasAddressChanged}
      ></ComplementaryInfosDrawer>

      {navigationGuardDialog}
    </>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = GeneralInformation
