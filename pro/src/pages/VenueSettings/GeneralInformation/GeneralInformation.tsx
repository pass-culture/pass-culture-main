import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation } from 'react-router'

import type { AdresseData } from '@/apiClient/adresse/types'
import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import type {
  ActivityNotOpenToPublic,
  ActivityOpenToPublic,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveStep } from '@/commons/hooks/useActiveStep'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useKey } from '@/commons/hooks/useKey'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
import { ActivityNotOpenToPublicMap } from '@/commons/mappings/ActivityNotOpenToPublic'
import { ActivityOpenToPublicMap } from '@/commons/mappings/ActivityOpenToPublic'
import { getMapKeys } from '@/commons/mappings/helpers'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { resetReactHookFormAddressFields } from '@/commons/utils/resetAddressFields'
import { scrollToTop } from '@/commons/utils/scrollToTop'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { AddressFields } from '@/components/AddressFields/AddressFields'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { MandatoryInfo } from '@/components/FormLayout/FormLayoutMandatoryInfo'
import { OpenToPublicToggle } from '@/components/OpenToPublicToggle/OpenToPublicToggle'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { STEP_NAMES } from '@/components/SettingsTabs/constants'
import { ActivityDetails } from '@/components/VenueEdition/ActivityDetails/ActivityDetails'
import { VenueFormActionBar } from '@/components/VenueEdition/VenueFormActionBar/VenueFormActionBar'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { AddressManual } from '@/ui-kit/form/AddressManual/AddressManual'
import { getPanelId, getTabId } from '@/ui-kit/Tabs/Tabs'

import { venueSettingsValidationSchema } from './commons/schema'
import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from './commons/types'
import { toBody } from './commons/utils/toBody'
import { toFormValues } from './commons/utils/toFormValues'
import { AddressChangeDialog } from './components/AddressChangeDialog/AddressChangeDialog'
import { ComplementaryInfosDialog } from './components/ComplementaryInfosDialog/ComplementaryInfosDialog'
import { ComplementaryInfosDrawer } from './components/ComplementaryInfosDrawer/ComplementaryInfosDrawer'
import { ReimbursementFields } from './components/ReimbursementFields/ReimbursementFields'
import { SiretOrCommentFields } from './components/SiretOrCommentFields/SiretOrCommentFields'

const GeneralInformation = () => {
  const venue = useAppSelector(ensureSelectedPartnerVenue)
  const isClosed = withVenueHelpers(venue).isClosed
  const addressFieldKey = useKey()
  const activeStep = useActiveStep(STEP_NAMES)
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const { syncVenueWithData } = useSyncVenueCache()

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

  const [isAddressChangeDialogOpen, setIsAddressChangeDialogOpen] =
    useState(false)
  const [isComplementaryInfosDrawerOpen, setIsComplementaryInfosDrawerOpen] =
    useState(false)
  const [isComplementaryInfosDialogOpen, setIsComplementaryInfosDialogOpen] =
    useState(false)
  const [hasAddressChanged, setHasAddressChanged] = useState(false)
  const onCancel = () => {
    form.reset()
    scrollToTop()
  }

  const openFollowUpDialogs = (formValues: VenueSettingsFormValues) => {
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
    const shouldOpenModal =
      shouldShowAddressChangeWarning || hasSiretChanged || hasBecomeOpenToPublic

    setHasAddressChanged(hasAddressChanged)
    if (shouldShowAddressChangeWarning && !hasSiretChanged) {
      setIsAddressChangeDialogOpen(true)
    }
    if (hasSiretChanged) {
      setIsComplementaryInfosDrawerOpen(true)
    }
    if (hasBecomeOpenToPublic) {
      setIsComplementaryInfosDialogOpen(true)
    }

    return shouldOpenModal
  }

  const handleSaveError = (error: unknown) => {
    if (isErrorAPIError(error) && error.status < 500) {
      snackBar.error(
        [
          'Une ou plusieurs erreurs sont présentes dans le formulaire',
          ...('global' in error.body ? error.body.global : []),
        ].join('\n')
      )
      serializeApiErrors(error.body, form.setError)
    } else {
      snackBar.error('Erreur lors de la sauvegarde de la structure.')
    }

    logEvent(Events.CLICKED_SAVE_VENUE, {
      saved: false,
      isEdition: true,
    })
  }

  const onSubmit = async (
    formValues: VenueSettingsFormValues
  ): Promise<boolean> => {
    try {
      const updatedVenue = await api.editVenue({
        path: { venue_id: Number(venue.id) },
        body: toBody(formValues, formContext),
      })
      await syncVenueWithData(venue.id, updatedVenue)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: true,
        isEdition: true,
      })
      snackBar.success('Vos modifications ont été sauvegardées')
    } catch (error) {
      handleSaveError(error)
      scrollToTop()
      return false
    }

    const shouldOpenModal = openFollowUpDialogs(formValues)
    // The main form has been successfully saved.
    // Reset it so the navigation guard does not reopen while handling
    // follow-up complementary information dialogs.
    form.reset(formValues)
    scrollToTop()
    return !shouldOpenModal
  }

  const {
    register,
    setValue,
    watch,
    clearErrors,
    formState: { isSubmitting, errors, disabled },
  } = form

  const {
    hasPendingNavigation,
    navigationGuardDialog,
    navigationGuardedSubmitHandler,
    proceedWithPendingNavigation,
  } = useFormNavigationGuard({ form, onSubmit })

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

    form.setValue('isOpenToPublic', isOpenToPublicValue, { shouldDirty: true })

    if (isOpenToPublicValue === 'false') {
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
    <div
      id={getPanelId(activeStep)}
      role="tabpanel"
      aria-labelledby={getTabId(activeStep)}
    >
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
                  disabled={isClosed}
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

              <FormLayout.Row mdSpaceAfter>
                <TextInput
                  {...register('publicName')}
                  label="Nom public"
                  description="À remplir si différent de la raison sociale. En le remplissant, c'est ce dernier qui sera visible du public."
                  disabled={isClosed}
                />
              </FormLayout.Row>

              <AddressFields
                key={addressFieldKey.value}
                label="Adresse de votre structure"
                addressRegister={register('addressAutocomplete')}
                disabled={disabled || isClosed}
                onAddressChosen={onAddressSelect}
                error={errors.addressAutocomplete?.message}
                renderManual={() => <AddressManual />}
                manual={manuallySetAddress}
                onManualChange={toggleManuallySetAddress}
              />
            </FormLayout.Section>

            <FormLayout.SubSection title="Accueil du public">
              <FormLayout.Row mdSpaceAfter>
                <OpenToPublicToggle
                  onChange={toggleOpenToPublic}
                  isOpenToPublic={isOpenToPublic}
                  disabled={isClosed}
                />
              </FormLayout.Row>
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
          <VenueFormActionBar
            disableFormSubmission={isClosed}
            isSubmitting={isSubmitting}
            onCancel={onCancel}
          />
        </form>
      </FormProvider>

      <AddressChangeDialog
        open={isAddressChangeDialogOpen}
        onOpenChange={(open) => {
          setIsAddressChangeDialogOpen(open)
          if (!open && hasPendingNavigation) {
            proceedWithPendingNavigation()
          }
        }}
      />

      <ComplementaryInfosDrawer
        open={isComplementaryInfosDrawerOpen}
        onOpenChange={(open) => {
          setIsComplementaryInfosDrawerOpen(open)
          if (!open && hasPendingNavigation) {
            proceedWithPendingNavigation()
          }
        }}
        hasAddressChanged={hasAddressChanged}
        onClose={() => {
          setIsComplementaryInfosDrawerOpen(false)
          if (hasPendingNavigation) {
            proceedWithPendingNavigation()
          }
        }}
      />

      <ComplementaryInfosDialog
        open={isComplementaryInfosDialogOpen}
        onOpenChange={setIsComplementaryInfosDialogOpen}
        openNextDialog={setIsComplementaryInfosDrawerOpen}
        onCancel={() => {
          if (hasPendingNavigation) {
            proceedWithPendingNavigation()
          }
        }}
      />
      {navigationGuardDialog}
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = GeneralInformation
