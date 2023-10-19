import { FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash/isEqual'
import React, { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import DialogBox from 'components/DialogBox'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { isOfferDisabled } from 'core/Offers/utils'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { getToday } from 'utils/date'
import { hasErrorCode } from 'utils/error'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import ActionBar from '../ActionBar/ActionBar'
import DialogStocksEventEditConfirm from '../DialogStocksEventEditConfirm/DialogStocksEventEditConfirm'
import useNotifyFormError from '../hooks/useNotifyFormError'
import { RecurrenceForm } from '../StocksEventCreation/RecurrenceForm'
import { getSuccessMessage } from '../utils/getSuccessMessage'

import { EventCancellationBanner } from './EventCancellationBanner'
import { getPriceCategoryOptions } from './getPriceCategoryOptions'
import { hasChangesOnStockWithBookings } from './hasChangesOnStockWithBookings'
import { STOCK_EVENT_FORM_DEFAULT_VALUES } from './StockFormList/constants'
import StockFormList from './StockFormList/StockFormList'
import {
  StockEventFormValues,
  StocksEventFormValues,
} from './StockFormList/types'
import { buildInitialValues } from './StockFormList/utils'
import { buildSingleInitialValues } from './StockFormList/utils/buildInitialValues'
import { getValidationSchema } from './StockFormList/validationSchema'
import styles from './StocksEventEdition.module.scss'
import { submitToApi } from './submitToApi'

const hasStocksChanged = (
  stocks: StockEventFormValues[],
  initialsStocks: StockEventFormValues[]
): boolean => {
  if (stocks.length !== initialsStocks.length) {
    return true
  }

  return stocks.some((stock) => {
    const initialStock = initialsStocks.find(
      (initialStock) => initialStock.stockId === stock.stockId
    )

    return !isEqual(stock, initialStock)
  })
}
export interface StocksEventEditionProps {
  offer: IndividualOffer
  stocks: StocksEvent[]
  setStocks: (stocks: StocksEvent[]) => void
}

const StocksEventEdition = ({
  offer,
  stocks,
  setStocks,
}: StocksEventEditionProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const notify = useNotification()
  const [showStocksEventConfirmModal, setShowStocksEventConfirmModal] =
    useState(false)
  const priceCategoriesOptions = getPriceCategoryOptions(offer.priceCategories)

  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)
  const onCancel = () => setIsRecurrenceModalOpen(false)
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departementCode
  )

  const setStocksInEditionForm = (stocksToAdd: StocksEvent[]) =>
    formik.setFieldValue('stocks', [
      ...stocksToAdd.map(
        (stock): StockEventFormValues =>
          buildSingleInitialValues({
            departementCode: offer.venue.departementCode || '',
            stock,
            today,
            lastProviderName: offer.lastProviderName,
            offerStatus: offer.status,
            priceCategoriesOptions,
          })
      ),
    ])

  // As we are using Formik to handle state and sorting/filtering, we need to
  // keep all the filtered out stocks in a variable somewhere so we don't lose them
  // This ref is where we keep track of all the filtered out stocks
  // Ideally it should be in the StockFormList component but it's not possible
  // because we need to re-integrate the filtered out stocks when we submit the form
  // We use a ref to prevent re-renreders and we forward it to the StockFormList component
  const hiddenStocksRef = useRef<StockEventFormValues[]>([])

  const onSubmit = async (values: StocksEventFormValues) => {
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.STOCKS
          : OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
    })

    // Return when saving in edition with an empty form
    const allStockValues = [...values.stocks, ...hiddenStocksRef.current]
    const isFormEmpty = allStockValues.every((val) =>
      isEqual(val, STOCK_EVENT_FORM_DEFAULT_VALUES)
    )
    // Return when there is nothing to save
    const dirty = hasStocksChanged(
      formik.values.stocks,
      formik.initialValues.stocks
    )
    if (isFormEmpty || !dirty) {
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Show modal if relevant
    const changesOnStockWithBookings = hasChangesOnStockWithBookings(
      allStockValues,
      formik.initialValues.stocks
    )
    if (!showStocksEventConfirmModal && changesOnStockWithBookings) {
      setShowStocksEventConfirmModal(true)
      return
    }

    // Submit
    try {
      await submitToApi(
        allStockValues,
        offer.id,
        offer.venue.departementCode ?? '',
        formik.setErrors,
        setStocksInEditionForm
      )
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error?.message)
      }
      return
    }

    navigate(nextStepUrl)
    notify.success(getSuccessMessage(mode))
    setShowStocksEventConfirmModal(false)
  }

  const onDeleteStock = async (
    stockValues: StockEventFormValues,
    stockIndex: number
  ) => {
    const { isDeletable, stockId } = stockValues
    // tested but coverage don't see it.
    /* istanbul ignore next */
    if (!isDeletable) {
      return
    }
    try {
      await api.deleteStock(stockId)

      // When we delete a stock we must remove it from the initial values
      // otherwise it will trigger the routeLeavingGuard
      const initialStocks = [...formik.initialValues.stocks]
      initialStocks.splice(stockIndex, 1)
      formik.resetForm({
        values: { stocks: initialStocks },
      })

      /* istanbul ignore next: DEBT, TO FIX */
      const formStocks = [...formik.values.stocks]
      formStocks.splice(stockIndex, 1)
      await formik.setValues({ stocks: formStocks })
      notify.success('Le stock a été supprimé.')
    } catch (error) {
      if (
        hasErrorCode(error) &&
        error.body.code === 'STOCK_FROM_CHARLIE_API_CANNOT_BE_DELETED'
      ) {
        notify.error(
          'La suppression des stocks de cette offre n’est possible que depuis le logiciel synchronisé.'
        )
      } else {
        notify.error('Une erreur est survenue lors de la suppression du stock.')
      }
    }
  }

  const initialValues = buildInitialValues({
    departementCode: offer.venue.departementCode,
    offerStocks: stocks,
    today,
    lastProviderName: offer.lastProviderName,
    offerStatus: offer.status,
    priceCategoriesOptions,
  })

  const formik = useFormik<StocksEventFormValues>({
    initialValues,
    onSubmit,
    validationSchema: getValidationSchema(priceCategoriesOptions),
  })

  // Replace formik.dirty who was true when it should not be
  const areStocksChanged = hasStocksChanged(
    formik.values.stocks,
    formik.initialValues.stocks
  )

  useNotifyFormError({
    isSubmitting: formik.isSubmitting,
    errors: formik.errors,
  })

  const handleBackToReadOnly = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
      })
    )
  }

  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const isSynchronized = Boolean(offer.lastProvider)

  return (
    <FormikProvider value={formik}>
      {showStocksEventConfirmModal && (
        <DialogStocksEventEditConfirm
          onConfirm={formik.submitForm}
          onCancel={() => setShowStocksEventConfirmModal(false)}
        />
      )}

      <FormLayout>
        <div aria-current="page">
          <form onSubmit={formik.handleSubmit} data-testid="stock-event-form">
            <EventCancellationBanner offer={offer} />

            <div className={styles['add-dates-button']}>
              <Button
                variant={ButtonVariant.PRIMARY}
                icon={fullMoreIcon}
                onClick={() => setIsRecurrenceModalOpen(true)}
                disabled={isSynchronized || isDisabled}
              >
                Ajouter une ou plusieurs dates
              </Button>
            </div>

            {isRecurrenceModalOpen && (
              <DialogBox
                onDismiss={onCancel}
                hasCloseButton
                labelledBy="add-recurrence"
                fullContentWidth
              >
                <RecurrenceForm
                  stocks={stocks}
                  offerId={offer.id}
                  setStocks={setStocks}
                  departmentCode={offer.venue.departementCode ?? ''}
                  priceCategories={offer.priceCategories ?? []}
                  setIsOpen={setIsRecurrenceModalOpen}
                  setStocksInEditionForm={setStocksInEditionForm}
                />
              </DialogBox>
            )}

            <StockFormList
              offer={offer}
              onDeleteStock={onDeleteStock}
              priceCategoriesOptions={priceCategoriesOptions}
              hiddenStocksRef={hiddenStocksRef}
            />

            <ActionBar
              isDisabled={formik.isSubmitting || isOfferDisabled(offer.status)}
              onClickPrevious={handleBackToReadOnly}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
            />
          </form>
        </div>
      </FormLayout>

      <RouteLeavingGuardIndividualOffer
        when={areStocksChanged && !formik.isSubmitting}
      />
    </FormikProvider>
  )
}

export default StocksEventEdition
