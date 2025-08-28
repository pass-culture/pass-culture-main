import { yupResolver } from '@hookform/resolvers/yup'
import { FormProvider, useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from '@/commons/core/Finances/constants'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled as getIsOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { DuoCheckbox } from '@/components/DuoCheckbox/DuoCheckbox'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { getSuccessMessage } from '@/components/IndividualOffer/utils/getSuccessMessage'
import { RouteLeavingGuardIndividualOffer } from '@/components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { ActionBar } from '@/pages/IndividualOffer/components/ActionBar/ActionBar'

import {
  type PriceTableFormValues,
  PriceTableValidationSchema,
} from '../commons/schemas'
import type { PriceTableFormContext } from '../commons/types'
import { saveEventOfferPriceTable } from '../commons/utils/saveEventOfferPriceTable'
import { saveNonEventOfferPriceTable } from '../commons/utils/saveNonEventOfferPriceTable'
import { toFormValues } from '../commons/utils/toFormValues'
import { ActivationCodeCallout } from './ActivationCodeCallout'
import { NonRefundableCallout } from './NonRefundableCallout'
import { PriceTableForm } from './PriceTableForm/PriceTableForm'

interface IndividualOfferPriceTableScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
  offerStocks: GetOfferStockResponseModel[]
}
export const IndividualOfferPriceTableScreen = ({
  offer,
  offerStocks,
}: IndividualOfferPriceTableScreenProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const notify = useNotification()
  const { subCategories, hasPublishedOfferWithSameEan } =
    useIndividualOfferContext()
  const { mutate } = useSWRConfig()
  const isMediaPageEnabled = useActiveFeature('WIP_ADD_VIDEO')
  const isCaledonian = useIsCaledonian()

  const offerSubcategory = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )
  assertOrFrontendError(
    offerSubcategory,
    '`offerSubcategory` not found in subcategories.'
  )

  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isOfferDisabled =
    getIsOfferDisabled(offer.status) || hasPublishedOfferWithSameEan
  const schemaValidationContext: PriceTableFormContext = {
    isCaledonian,
    mode,
    offer,
  }

  const form = useForm({
    context: schemaValidationContext,
    defaultValues: toFormValues(
      offer,
      offer.isEvent ? (offer.priceCategories ?? []) : offerStocks,
      schemaValidationContext
    ),
    mode: 'onBlur',
    resolver: yupResolver(PriceTableValidationSchema),
  })

  // TODO (igabriele, 2025-08-22): Move that into a hook.
  const onSubmit = async (formValues: PriceTableFormValues): Promise<void> => {
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
          : offer.isEvent
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
      isOnboarding,
    })

    if (!form.formState.isDirty && mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(nextStepUrl)

      notify.success(getSuccessMessage(mode))

      return
    }

    try {
      if (offer.isEvent) {
        await saveEventOfferPriceTable(formValues, { offer })
      } else {
        await saveNonEventOfferPriceTable(formValues, {
          offer,
          setError: form.setError,
        })
      }
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error.message)
      }
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offer.id])

    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(getSuccessMessage(mode))
    }

    navigate(nextStepUrl)
  }

  const handlePreviousStepOrBackToReadOnly = () => {
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.READ_ONLY,
          isOnboarding,
        })
      )
    } else {
      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: isMediaPageEnabled
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
          mode,
          isOnboarding,
        })
      )
    }
  }

  return (
    <>
      <FormProvider {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          data-testid="stock-thing-form"
        >
          <FormLayout>
            <FormLayout.MandatoryInfo />

            <FormLayout.Section title="Tarifs">
              {offerSubcategory.reimbursementRule ===
                REIMBURSEMENT_RULES.NOT_REIMBURSED && <NonRefundableCallout />}
              {offer.isDigital && <ActivationCodeCallout />}

              <PriceTableForm
                isCaledonian={isCaledonian}
                isReadOnly={isOfferDisabled}
                mode={mode}
                offer={offer}
                schemaValidationContext={schemaValidationContext}
              />
            </FormLayout.Section>
          </FormLayout>

          {offer.isEvent && (
            <FormLayout fullWidthActions>
              <FormLayout.Section title="Réservations “Duo”">
                <DuoCheckbox
                  {...form.register('isDuo')}
                  checked={Boolean(form.watch('isDuo'))}
                  disabled={isOfferDisabled}
                />
              </FormLayout.Section>
            </FormLayout>
          )}

          <ActionBar
            onClickPrevious={handlePreviousStepOrBackToReadOnly}
            step={INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS}
            isDisabled={
              form.formState.isSubmitting ||
              isOfferDisabled ||
              !!hasPublishedOfferWithSameEan
            }
            dirtyForm={form.formState.isDirty}
            isEvent={false}
          />
        </form>
      </FormProvider>

      <RouteLeavingGuardIndividualOffer
        when={form.formState.isDirty && !form.formState.isSubmitting}
      />
    </>
  )
}
