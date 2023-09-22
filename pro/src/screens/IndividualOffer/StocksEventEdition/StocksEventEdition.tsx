import { format } from 'date-fns'
import { FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash/isEqual'
import React, { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { PriceCategoryResponseModel } from 'apiClient/v1'
import DialogBox from 'components/DialogBox'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { isOfferDisabled } from 'core/Offers/utils'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { SelectOption } from 'custom_types/form'
import { useOfferWizardMode } from 'hooks'
import useNotification from 'hooks/useNotification'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { FORMAT_HH_mm, FORMAT_ISO_DATE_ONLY, getToday } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { ActionBar } from '../ActionBar'
import { MAX_STOCKS_PER_OFFER } from '../constants'
import DialogStocksEventEditConfirm from '../DialogStocksEventEditConfirm/DialogStocksEventEditConfirm'
import { useNotifyFormError } from '../hooks'
import { RecurrenceForm } from '../StocksEventCreation/RecurrenceForm'
import { getSuccessMessage } from '../utils'

import { upsertStocksEventAdapter } from './adapters'
import { serializeStockEventEdition } from './adapters/serializers'
import { EventCancellationBanner } from './EventCancellationBanner'
import {
  buildInitialValues,
  getValidationSchema,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
  StockEventFormValues,
  StockFormList,
} from './StockFormList'
import styles from './StocksEventEdition.module.scss'

export const hasChangesOnStockWithBookings = (
  submittedStocks: StockEventFormValues[],
  initialStocks: StockEventFormValues[]
) => {
  const initialStocksById: Record<
    string,
    Partial<StockEventFormValues>
  > = initialStocks.reduce(
    (dict: Record<string, Partial<StockEventFormValues>>, stock) => {
      dict[stock.stockId || 'StockEventFormValuesnewStock'] = {
        priceCategoryId: stock.priceCategoryId,
        beginningDate: stock.beginningDate,
        beginningTime: stock.beginningTime,
      }
      return dict
    },
    {}
  )

  return submittedStocks.some(stock => {
    if (
      !stock.bookingsQuantity ||
      stock.bookingsQuantity === 0 ||
      !stock.stockId
    ) {
      return false
    }
    const initialStock = initialStocksById[stock.stockId]
    const fieldsWithWarning: (keyof StockEventFormValues)[] = [
      'priceCategoryId',
      'beginningDate',
      'beginningTime',
    ]

    return fieldsWithWarning.some(
      (fieldName: keyof StockEventFormValues) =>
        initialStock[fieldName] !== stock[fieldName]
    )
  })
}

const hasStocksChanged = (
  stocks: StockEventFormValues[],
  initialsStocks: StockEventFormValues[]
): boolean => {
  if (stocks.length !== initialsStocks.length) {
    return true
  }

  return stocks.some(stock => {
    const initialStock = initialsStocks.find(
      initialStock => initialStock.stockId === stock.stockId
    )

    return !isEqual(stock, initialStock)
  })
}

export const getPriceCategoryOptions = (
  priceCategories?: PriceCategoryResponseModel[] | null
): SelectOption[] => {
  // Clone list to avoid mutation
  const newPriceCategories = [...(priceCategories ?? [])]
  newPriceCategories.sort((a, b) => {
    if (a.price === b.price) {
      return a.label.localeCompare(b.label)
    }
    return a.price - b.price
  })

  return (
    newPriceCategories?.map(
      (priceCategory): SelectOption => ({
        label: `${formatPrice(priceCategory.price)} - ${priceCategory.label}`,
        value: priceCategory.id,
      })
    ) ?? []
  )
}

export interface StocksEventEditionProps {
  offer: IndividualOffer
}

const StocksEventEdition = ({
  offer,
}: StocksEventEditionProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const [afterSubmitUrl, setAfterSubmitUrl] = useState<string>(
    getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? OFFER_WIZARD_STEP_IDS.STOCKS
          : OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
    })
  )
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const navigate = useNavigate()
  const notify = useNotification()
  const { setOffer } = useIndividualOfferContext()
  const [showStocksEventConfirmModal, setShowStocksEventConfirmModal] =
    useState(false)
  const priceCategoriesOptions = getPriceCategoryOptions(offer.priceCategories)

  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)
  const onCancel = () => setIsRecurrenceModalOpen(false)
  const onConfirm = (newStocks: StocksEvent[]) => {
    setIsRecurrenceModalOpen(false)
    const transformedStocks = newStocks.map(
      (stock): StockEventFormValues => ({
        priceCategoryId: String(stock.priceCategoryId),
        bookingsQuantity: 0,
        remainingQuantity: stock.quantity ?? '',
        isDeletable: true,
        beginningDate: format(
          new Date(stock.beginningDatetime),
          FORMAT_ISO_DATE_ONLY
        ),
        beginningTime: format(new Date(stock.beginningDatetime), FORMAT_HH_mm),
        bookingLimitDatetime: format(
          new Date(stock.bookingLimitDatetime),
          FORMAT_ISO_DATE_ONLY
        ),
        readOnlyFields: [],
      })
    )
    const rawStocksToAdd = [...formik.values.stocks, ...transformedStocks]

    // deduplicate stocks in the whole list
    const stocksToAdd = rawStocksToAdd.filter((stock1, index) => {
      return (
        rawStocksToAdd.findIndex(
          stock2 =>
            stock1.beginningDate === stock2.beginningDate &&
            stock1.beginningTime === stock2.beginningTime &&
            stock1.priceCategoryId === stock2.priceCategoryId
        ) === index
      )
    })
    if (stocksToAdd.length < rawStocksToAdd.length) {
      notify.information(
        'Certaines occurences n’ont pas été ajoutées car elles existaient déjà'
      )
    } else {
      notify.success(
        newStocks.length === 1
          ? '1 nouvelle occurrence a été ajoutée'
          : `${newStocks.length} nouvelles occurrences ont été ajoutées`
      )
    }
    formik.setFieldValue('stocks', [...stocksToAdd])
  }

  // As we are using Formik to handle state and sorting/filtering, we need to
  // keep all the filtered out stocks in a variable somewhere so we don't lose them
  // This ref is where we keep track of all the filtered out stocks
  // Ideally it should be in the StockFormList component but it's not possible
  // because we need to re-integrate the filtered out stocks when we submit the form
  // We use a ref to prevent re-renreders and we forward it to the StockFormList component
  const hiddenStocksRef = useRef<StockEventFormValues[]>([])

  const onSubmit = async (formValues: { stocks: StockEventFormValues[] }) => {
    const allStocks = [...formValues.stocks, ...hiddenStocksRef.current]
    const changesOnStockWithBookings = hasChangesOnStockWithBookings(
      allStocks,
      formik.initialValues.stocks
    )

    if (!showStocksEventConfirmModal && changesOnStockWithBookings) {
      setShowStocksEventConfirmModal(true)
      return
    } else {
      setShowStocksEventConfirmModal(false)
    }

    if (allStocks.length > MAX_STOCKS_PER_OFFER) {
      notify.error(
        `Veuillez créer moins de ${MAX_STOCKS_PER_OFFER} occurrences par offre.`
      )
      return
    }

    const { isOk, payload } = await upsertStocksEventAdapter({
      offerId: offer.id,
      stocks: serializeStockEventEdition(allStocks, offer.venue.departmentCode),
    })

    /* istanbul ignore next: DEBT, TO FIX */
    if (isOk) {
      const response = await getIndividualOfferAdapter(offer.id)
      if (response.isOk) {
        const updatedOffer = response.payload
        setOffer && setOffer(updatedOffer)
        formik.resetForm({
          values: buildInitialValues({
            departmentCode: updatedOffer.venue.departmentCode,
            offerStocks: updatedOffer.stocks,
            today,
            lastProviderName: updatedOffer.lastProviderName,
            offerStatus: updatedOffer.status,
            priceCategoriesOptions,
          }),
        })
      }
      navigate(afterSubmitUrl)
      notify.success(getSuccessMessage(mode))
    } else {
      /* istanbul ignore next: DEBT, TO FIX */
      formik.setErrors({ stocks: payload.errors })
    }
    setIsClickingFromActionBar(false)
  }

  const onDeleteStock = async (
    stockValues: StockEventFormValues,
    stockIndex: number
  ) => {
    const { isDeletable, stockId } = stockValues
    // tested but coverage don't see it.
    /* istanbul ignore next */
    if (stockId === undefined || !isDeletable) {
      return
    }
    try {
      await api.deleteStock(stockId)
      const response = await getIndividualOfferAdapter(offer.id)
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }

      const formStocks = [...formik.values.stocks]

      // When we delete a stock we must remove it from the initial values
      // otherwise it will trigger the routeLeavingGuard
      const initialStocks = [...formik.initialValues.stocks]
      initialStocks.splice(stockIndex, 1)
      formik.resetForm({
        values: { stocks: initialStocks },
      })

      // Set back possible user change.
      /* istanbul ignore next: DEBT, TO FIX */
      formStocks.splice(stockIndex, 1)
      formik.setValues({ stocks: formStocks })
      notify.success('Le stock a été supprimé.')
    } catch {
      notify.error('Une erreur est survenue lors de la suppression du stock.')
    }
  }

  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departmentCode
  )

  const initialValues = buildInitialValues({
    departmentCode: offer.venue.departmentCode,
    offerStocks: offer.stocks,
    today,
    lastProviderName: offer.lastProviderName,
    offerStatus: offer.status,
    priceCategoriesOptions,
  })

  const formik = useFormik<{ stocks: StockEventFormValues[] }>({
    initialValues,
    onSubmit,
    validationSchema: getValidationSchema(priceCategoriesOptions),
  })

  // Replace formik.dirty who was true when it should not be
  const areStocksChanged = hasStocksChanged(
    formik.values.stocks,
    formik.initialValues.stocks
  )

  const isFormEmpty = () => {
    const allStockValues = [...formik.values.stocks, ...hiddenStocksRef.current]
    return allStockValues.every(val =>
      isEqual(val, STOCK_EVENT_FORM_DEFAULT_VALUES)
    )
  }

  useNotifyFormError({
    isSubmitting: formik.isSubmitting,
    errors: formik.errors,
  })

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      setIsClickingFromActionBar(true)
      if (Object.keys(formik.errors).length !== 0) {
        /* istanbul ignore next: DEBT, TO FIX */
        setIsClickingFromActionBar(false)
      }

      const nextStepUrl = getIndividualOfferUrl({
        offerId: offer.id,
        step:
          saveDraft || mode === OFFER_WIZARD_MODE.EDITION
            ? OFFER_WIZARD_STEP_IDS.STOCKS
            : OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode:
          mode === OFFER_WIZARD_MODE.EDITION
            ? OFFER_WIZARD_MODE.READ_ONLY
            : mode,
      })

      // When saving draft with an empty form
      // we display a success notification even if nothing is done
      if (isFormEmpty()) {
        setIsClickingFromActionBar(false)
        if (saveDraft) {
          notify.success('Brouillon sauvegardé dans la liste des offres')
          return
        } else {
          navigate(nextStepUrl)
          notify.success(getSuccessMessage(mode))
        }
      }
      // tested but coverage don't see it.
      /* istanbul ignore next */
      setAfterSubmitUrl(nextStepUrl)

      const allStockValues = [
        ...formik.values.stocks,
        ...hiddenStocksRef.current,
      ]
      const hasSavedStock = allStockValues.some(
        stock => stock.stockId !== undefined
      )

      /* istanbul ignore next: DEBT, TO FIX */
      if (hasSavedStock && !formik.dirty) {
        setIsClickingFromActionBar(false)
        /* istanbul ignore next: DEBT to fix */
        if (!saveDraft) {
          navigate(nextStepUrl)
        }
        /* istanbul ignore next: DEBT to fix */
        notify.success(getSuccessMessage(mode))
        setIsClickingFromActionBar(false)
      } else {
        if (saveDraft) {
          await formik.submitForm()
        }
      }
    }

  useEffect(() => {
    if (!formik.isValid) {
      setIsClickingFromActionBar(false)
    }
  }, [formik.isValid])

  const handlePreviousStep = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
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
                  offer={offer}
                  onCancel={onCancel}
                  onConfirm={onConfirm}
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
              onClickNext={handleNextStep()}
              onClickPrevious={handlePreviousStep}
              onClickSaveDraft={handleNextStep({ saveDraft: true })}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
              submitAsButton={isFormEmpty()}
            />
          </form>
        </div>
      </FormLayout>

      <RouteLeavingGuardIndividualOffer
        when={areStocksChanged && !isClickingFromActionBar}
        isEdition
      />
    </FormikProvider>
  )
}

export default StocksEventEdition
