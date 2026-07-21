import { yupResolver } from '@hookform/resolvers/yup'
import { useRef, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { getAfterSubmitPath } from '@/pages/IndividualOffer/commons/utils/getAfterSubmitPath'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'

import { UpdateWarningDialog } from '../../IndividualOfferLocation/components/UpdateWarningDialog/UpdateWarningDialog'
import { getInitialValuesFromOffer } from '../commons/getInitialValuesFromOffer'
import { getPatchOfferBody } from '../commons/getPatchOfferBody'
import type { IndividualOfferPracticalInfosFormValues } from '../commons/types'
import { getValidationSchema } from '../commons/validationSchema'
import { IndividualOfferPracticalInfosForm } from './IndividualOfferPracticalInfosForm/IndividualOfferPracticalInfosForm'

export type IndividualOfferPracticalInfosScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  stocks: GetOfferStockResponseModel[]
}

export const IndividualOfferPracticalInfosScreen = ({
  offer,
  stocks,
}: IndividualOfferPracticalInfosScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')
  const mode = useOfferWizardMode()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isVenueClosed = withVenueHelpers(selectedPartnerVenue).isClosed

  const snackBar = useSnackBar()

  const { subCategories } = useIndividualOfferContext()

  const subCategory = subCategories.find(
    (cat) => cat.id === offer?.subcategoryId
  )

  const [isUpdateWarningDialogOpen, setIsUpdateWarningDialogOpen] =
    useState(false)

  const saveEditionChangesButtonRef = useRef<HTMLButtonElement>(null)

  const form = useForm<IndividualOfferPracticalInfosFormValues>({
    defaultValues: getInitialValuesFromOffer(offer, subCategory),
    resolver: yupResolver(getValidationSchema(subCategory?.canBeWithdrawable)),
    mode: 'onBlur',
  })

  const handlePreviousStep = async () => {
    if (mode === OFFER_WIZARD_MODE.CREATION) {
      await navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: offer.isEvent
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.CREATION,
          isOnboarding,
        })
      )
    } else {
      await navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
          isOfferExposureEnabled,
        })
      )
    }
  }

  const updateWarningDialogCallbackRef = useRef<
    ((shouldSendMail: boolean | null) => void) | null
  >(null)

  const onSubmit = async (
    formValues: IndividualOfferPracticalInfosFormValues
  ): Promise<boolean> => {
    const hasModifiedWithdrawalInfos = (
      [
        'withdrawalDetails',
        'withdrawalDelay',
        'withdrawalType',
      ] as (keyof IndividualOfferPracticalInfosFormValues)[]
    ).some(
      (field) => form.getValues(field) !== form.formState.defaultValues?.[field]
    )

    let shouldSendMail = false

    if (offer.hasPendingBookings && hasModifiedWithdrawalInfos) {
      setIsUpdateWarningDialogOpen(true)
      const choice = await new Promise<boolean | null>((callback) => {
        updateWarningDialogCallbackRef.current = callback
      })
      setIsUpdateWarningDialogOpen(false)

      if (choice === null) {
        return false
      }
      shouldSendMail = choice
    }

    try {
      const requestBody = getPatchOfferBody(formValues, shouldSendMail)

      await mutate(
        [GET_OFFER_QUERY_KEY, offer.id],
        // TODO (rchaffal) to remove once PatchOfferBodyModel is migrated to Pydantic V2
        // @ts-expect-error
        api.patchOffer({ path: { offer_id: offer.id }, body: requestBody }),
        { revalidate: false }
      )

      form.reset(formValues)

      if (isOfferExposureEnabled && mode === OFFER_WIZARD_MODE.EDITION) {
        snackBar.success('Votre offre a bien été modifiée.')
      }

      return true
    } catch {
      snackBar.error(SENT_DATA_ERROR_MESSAGE)

      return false
    }
  }

  const afterSubmitPath = () =>
    getAfterSubmitPath({
      offerId: offer.id,
      mode,
      isOnboarding,
      isOfferExposureEnabled,
      currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
      followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
    })
  const { navigationGuardedSubmitHandler, navigationGuardDialog } =
    useFormNavigationGuard({
      afterSubmitPath,
      form,
      onSubmit,
    })

  return (
    <>
      {isUpdateWarningDialogOpen && (
        <UpdateWarningDialog
          onCancel={() => updateWarningDialogCallbackRef.current?.(null)}
          onConfirm={(shouldSendMail) =>
            updateWarningDialogCallbackRef.current?.(shouldSendMail)
          }
          refToFocusOnClose={saveEditionChangesButtonRef}
          message="Vous avez modifié les modalités de retrait."
        />
      )}
      <FormProvider {...form}>
        <form onSubmit={navigationGuardedSubmitHandler} noValidate>
          <ScrollToFirstHookFormErrorAfterSubmit />
          <IndividualOfferPracticalInfosForm
            offer={offer}
            subCategory={subCategory}
            stocks={stocks}
          />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS}
            isDisabled={
              form.formState.isSubmitting ||
              isOfferDisabled(offer) ||
              (!form.formState.isDirty &&
                mode !== OFFER_WIZARD_MODE.CREATION) ||
              isVenueClosed
            }
            saveEditionChangesButtonRef={saveEditionChangesButtonRef}
          />
        </form>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}
