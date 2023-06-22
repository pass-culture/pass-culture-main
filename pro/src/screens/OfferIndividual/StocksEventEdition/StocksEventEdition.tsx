import { FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash/isEqual'
import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { PriceCategoryResponseModel } from 'apiClient/v1'
import DialogBox from 'components/DialogBox'
import FormLayout, { FormLayoutDescription } from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { RouteLeavingGuardOfferIndividual } from 'components/RouteLeavingGuardOfferIndividual'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { isOfferDisabled } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { SelectOption } from 'custom_types/form'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { PlusCircleIcon } from 'icons'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { getToday } from 'utils/date'
import { formatPrice } from 'utils/formatPrice'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { ActionBar } from '../ActionBar'
import DialogStocksEventEditConfirm from '../DialogStocksEventEditConfirm/DialogStocksEventEditConfirm'
import { useNotifyFormError } from '../hooks'
import { RecurrenceForm } from '../StocksEventCreation/RecurrenceForm'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos'
import { getSuccessMessage } from '../utils'
import { logTo } from '../utils/logTo'

import { upsertStocksEventAdapter } from './adapters'
import { serializeStockEventEdition } from './adapters/serializers'
import {
  getValidationSchema,
  buildInitialValues,
  StockEventFormValues,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
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
  offer: IOfferIndividual
}

const StocksEventEdition = ({
  offer,
}: StocksEventEditionProps): JSX.Element => {
  const mode = useOfferWizardMode()
  const [afterSubmitUrl, setAfterSubmitUrl] = useState<string>(
    getOfferIndividualUrl({
      offerId: offer.nonHumanizedId,
      step: OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode,
    })
  )
  const [isClickingFromActionBar, setIsClickingFromActionBar] =
    useState<boolean>(false)
  const [isSubmittingDraft, setIsSubmittingDraft] = useState<boolean>(false)
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const notify = useNotification()
  const { setOffer, shouldTrack, setShouldTrack } = useOfferIndividualContext()
  const providerName = offer?.lastProviderName
  const [showStocksEventConfirmModal, setShowStocksEventConfirmModal] =
    useState(false)
  const priceCategoriesOptions = getPriceCategoryOptions(offer.priceCategories)

  let description
  let links

  if (!isOfferDisabled(offer.status)) {
    description =
      'Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’évènement. \n Vous pouvez annuler un évènement en supprimant la ligne de stock associée. Cette action est irréversible.'
    links = [
      {
        href: 'https://aide.passculture.app/hc/fr/articles/4411992053649--Acteurs-Culturels-Comment-annuler-ou-reporter-un-%C3%A9v%C3%A9nement-',
        linkTitle: 'Comment reporter ou annuler un évènement ?',
      },
    ]
  }

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
        beginningDate: new Date(stock.beginningDatetime),
        beginningTime: new Date(stock.beginningDatetime),
        bookingLimitDatetime: new Date(stock.bookingLimitDatetime),
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

    const { isOk, payload } = await upsertStocksEventAdapter({
      offerId: offer.nonHumanizedId,
      stocks: serializeStockEventEdition(allStocks, offer.venue.departmentCode),
    })

    /* istanbul ignore next: DEBT, TO FIX */
    if (isOk) {
      const response = await getOfferIndividualAdapter(offer.nonHumanizedId)
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
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.STOCKS,
        to: isSubmittingDraft
          ? OFFER_WIZARD_STEP_IDS.STOCKS
          : OFFER_WIZARD_STEP_IDS.SUMMARY,
        used: isSubmittingDraft
          ? OFFER_FORM_NAVIGATION_MEDIUM.DRAFT_BUTTONS
          : OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: true,
        isDraft: false,
        offerId: offer.nonHumanizedId,
      })
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
      const response = await getOfferIndividualAdapter(offer.nonHumanizedId)
      /* istanbul ignore next: DEBT, TO FIX */
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }

      const formStocks = [...formik.values.stocks, ...hiddenStocksRef.current]

      // When we delete a stock we must remove it from the initial values
      // otherwise it will trigger the routeLeavingGuard
      const initalStocks = [...formik.initialValues.stocks]
      initalStocks.splice(stockIndex, 1)
      formik.resetForm({
        values: { stocks: initalStocks },
      })

      // Set back possible user change.
      /* istanbul ignore next: DEBT, TO FIX */
      formStocks.splice(stockIndex, 1)
      /* istanbul ignore next: DEBT, TO FIX */
      formStocks.length
        ? formik.setValues({ stocks: formStocks })
        : formik.resetForm({
            values: { stocks: [STOCK_EVENT_FORM_DEFAULT_VALUES] },
          })
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

  useEffect(() => {
    // when form is dirty it's tracked by RouteLeavingGuard
    setShouldTrack(!formik.dirty)
  }, [formik.dirty])

  const handleNextStep =
    ({ saveDraft = false } = {}) =>
    async () => {
      setIsClickingFromActionBar(true)
      if (Object.keys(formik.errors).length !== 0) {
        /* istanbul ignore next: DEBT, TO FIX */
        setIsClickingFromActionBar(false)
      }

      const nextStepUrl = getOfferIndividualUrl({
        offerId: offer.nonHumanizedId,
        step: saveDraft
          ? OFFER_WIZARD_STEP_IDS.STOCKS
          : OFFER_WIZARD_STEP_IDS.SUMMARY,
        mode,
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
      setIsSubmittingDraft(saveDraft)
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
    if (!formik.dirty) {
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.STOCKS,
        to: OFFER_WIZARD_STEP_IDS.TARIFS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: true,
        isDraft: false,
        offerId: offer.nonHumanizedId,
      })
    }
    /* istanbul ignore next: DEBT, TO FIX */
    navigate(
      getOfferIndividualUrl({
        offerId: offer.nonHumanizedId,
        step: OFFER_WIZARD_STEP_IDS.TARIFS,
        mode,
      })
    )
  }

  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const isSynchronized = Boolean(offer.lastProvider)

  return (
    <FormikProvider value={formik}>
      {providerName && (
        <SynchronizedProviderInformation providerName={providerName} />
      )}

      {showStocksEventConfirmModal && (
        <DialogStocksEventEditConfirm
          onConfirm={formik.submitForm}
          onCancel={() => setShowStocksEventConfirmModal(false)}
        />
      )}

      <FormLayout>
        <div aria-current="page">
          <form onSubmit={formik.handleSubmit} data-testid="stock-event-form">
            <FormLayoutDescription
              description={description}
              links={links}
              isBanner
            />

            <div className={styles['add-dates-button']}>
              <Button
                variant={ButtonVariant.PRIMARY}
                Icon={PlusCircleIcon}
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
              offerId={offer.nonHumanizedId}
              shouldTrack={shouldTrack}
              submitAsButton={isFormEmpty()}
            />
          </form>
        </div>
      </FormLayout>

      <RouteLeavingGuardOfferIndividual
        when={formik.dirty && !isClickingFromActionBar}
        tracking={nextLocation =>
          logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            from: OFFER_WIZARD_STEP_IDS.STOCKS,
            to: logTo(nextLocation),
            used: OFFER_FORM_NAVIGATION_OUT.ROUTE_LEAVING_GUARD,
            isEdition: true,
            isDraft: false,
            offerId: offer?.nonHumanizedId,
          })
        }
      />
    </FormikProvider>
  )
}

export default StocksEventEdition
