import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from '@/commons/core/Finances/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useFormNavigationGuard } from '@/commons/hooks/useFormNavigationGuard/useFormNavigationGuard'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { DuoCheckbox } from '@/components/DuoCheckbox/DuoCheckbox'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { ScrollToFirstHookFormErrorAfterSubmit } from '@/components/ScrollToFirstErrorAfterSubmit/ScrollToFirstErrorAfterSubmit'
import { getAfterSubmitPath } from '@/pages/IndividualOffer/commons/utils/getAfterSubmitPath'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'

import { useSaveOfferPriceTable } from '../commons/hooks/useSaveOfferPriceTable'
import { PriceTableValidationSchema } from '../commons/schemas'
import type { PriceTableFormContext } from '../commons/types'
import { toFormValues } from '../commons/utils/toFormValues'
import { ActivationCodeCallout } from './ActivationCodeCallout'
import { NonRefundableCallout } from './NonRefundableCallout'
import { PriceTableForm } from './PriceTableForm/PriceTableForm'

interface IndividualOfferPriceTableScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
  offerStocks: GetOfferStockResponseModel[] | undefined
}
export const IndividualOfferPriceTableScreen = ({
  offer,
  offerStocks,
}: IndividualOfferPriceTableScreenProps) => {
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')
  const { subCategories, hasPublishedOfferWithSameEan } =
    useIndividualOfferContext()

  const isCaledonian = useIsCaledonian()

  const offerSubcategory = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )
  assertOrFrontendError(
    offerSubcategory,
    '`offerSubcategory` not found in subcategories.'
  )

  const isOnboarding = pathname.includes('onboarding')
  const schemaValidationContext: PriceTableFormContext = {
    isCaledonian,
    mode,
    offer,
  }

  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const form = useForm({
    context: schemaValidationContext,
    defaultValues: toFormValues(
      offer,
      offer.isEvent ? (offer.priceCategories ?? []) : (offerStocks ?? []),
      schemaValidationContext
    ),
    mode: 'onBlur',
    resolver: yupResolver(PriceTableValidationSchema),
  })

  const { save } = useSaveOfferPriceTable({
    form,
    offer,
  })

  const afterSubmitPath = getAfterSubmitPath({
    offerId: offer.id,
    mode,
    isOnboarding,
    isOfferExposureEnabled,
    currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
    followingStep: offer.isEvent
      ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE
      : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
  })
  const { navigationGuardedSubmitHandler, navigationGuardDialog } =
    useFormNavigationGuard({
      afterSubmitPath,
      form,
      onSubmit: save,
    })

  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
          isOfferExposureEnabled,
        })
      )
    } else {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
          mode,
          isOnboarding,
        })
      )
    }
  }

  return (
    <>
      <FormProvider {...form}>
        <form onSubmit={navigationGuardedSubmitHandler}>
          <ScrollToFirstHookFormErrorAfterSubmit />
          <FormLayout>
            <FormLayout.MandatoryInfo />

            <FormLayout.Section title="Tarifs">
              {offerSubcategory.reimbursementRule ===
                REIMBURSEMENT_RULES.NOT_REIMBURSED && <NonRefundableCallout />}
              {!offer.isEvent && offer.isDigital && <ActivationCodeCallout />}

              <PriceTableForm
                isCaledonian={isCaledonian}
                mode={mode}
                offer={offer}
                schemaValidationContext={schemaValidationContext}
              />
            </FormLayout.Section>
          </FormLayout>
          {canBeDuo && (
            <FormLayout fullWidthActions>
              <FormLayout.Section title="Réservations “Duo”">
                <DuoCheckbox
                  {...form.register('isDuo')}
                  checked={Boolean(form.watch('isDuo'))}
                  disabled={
                    isOfferDisabled(offer) ||
                    hasPublishedOfferWithSameEan ||
                    isOfferSynchronized(offer)
                  }
                />
              </FormLayout.Section>
            </FormLayout>
          )}
          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE}
            isDisabled={
              isOfferDisabled(offer) ||
              hasPublishedOfferWithSameEan ||
              form.formState.isSubmitting ||
              (isOfferExposureEnabled &&
                !form.formState.isDirty &&
                mode !== OFFER_WIZARD_MODE.CREATION)
            }
            dirtyForm={form.formState.isDirty}
            isEvent={false}
          />
        </form>
      </FormProvider>

      {navigationGuardDialog}
    </>
  )
}
