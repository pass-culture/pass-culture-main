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
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
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
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const mode = useOfferWizardMode()

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
        })
      )
    }
  }

  async function onSubmit(formValues: IndividualOfferPracticalInfosFormValues) {
    const shouldOpenWarningDialog =
      offer.hasPendingBookings &&
      (
        [
          'withdrawalDetails',
          'withdrawalDelay',
          'withdrawalType',
        ] as (keyof IndividualOfferPracticalInfosFormValues)[]
      ).some((field) => {
        return form.watch(field) !== form.formState.defaultValues?.[field]
      })

    if (shouldOpenWarningDialog) {
      setIsUpdateWarningDialogOpen(true)
    } else {
      await onContinue(formValues, false)
    }
  }

  async function onContinue(
    formValues: IndividualOfferPracticalInfosFormValues,
    shouldSendMail: boolean
  ) {
    try {
      const requestBody = getPatchOfferBody(formValues, shouldSendMail)

      await mutate(
        [GET_OFFER_QUERY_KEY, offer.id],
        api.patchOffer(offer.id, requestBody),
        { revalidate: false }
      )

      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY

      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: nextStep,
          mode:
            mode === OFFER_WIZARD_MODE.EDITION
              ? OFFER_WIZARD_MODE.READ_ONLY
              : mode,
          isOnboarding,
        })
      )
    } catch {
      snackBar.error(SENT_DATA_ERROR_MESSAGE)
      return
    }
  }

  return (
    <>
      {isUpdateWarningDialogOpen && (
        <UpdateWarningDialog
          onCancel={() => setIsUpdateWarningDialogOpen(false)}
          onConfirm={(shouldSendMail) => {
            form.handleSubmit((formValues) =>
              onContinue(formValues, shouldSendMail)
            )()
            setIsUpdateWarningDialogOpen(false)
          }}
          refToFocusOnClose={saveEditionChangesButtonRef}
          message="Vous avez modifié les modalités de retrait."
        />
      )}
      <FormProvider {...form}>
        <form
          onSubmit={form.handleSubmit((values) => onSubmit(values))}
          noValidate
        >
          <ScrollToFirstHookFormErrorAfterSubmit />
          <IndividualOfferPracticalInfosForm
            offer={offer}
            subCategory={subCategory}
            stocks={stocks}
          />
          <ActionBar
            onClickPrevious={handlePreviousStep}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS}
            isDisabled={form.formState.isSubmitting || isOfferDisabled(offer)}
            saveEditionChangesButtonRef={saveEditionChangesButtonRef}
          />
          <RouteLeavingGuardIndividualOffer
            when={form.formState.isDirty && !form.formState.isSubmitting}
          />
        </form>
      </FormProvider>
    </>
  )
}
