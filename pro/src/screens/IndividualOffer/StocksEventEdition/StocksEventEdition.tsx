import cn from 'classnames'
import { FieldArray, FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash/isEqual'
import React, { useRef, useState } from 'react'
import { Pagination } from 'react-instantsearch'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { StocksOrderedBy } from 'apiClient/v1'
import DialogBox from 'components/DialogBox'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { StockFormActions } from 'components/StockFormActions'
import { FilterResultsRow } from 'components/StocksEventList/FilterResultsRow'
import { NoResultsRow } from 'components/StocksEventList/NoResultsRow'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import {
  STOCKS_PER_PAGE,
  StocksEvent,
} from 'components/StocksEventList/StocksEventList'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { IndividualOffer } from 'core/Offers/types'
import { isOfferDisabled } from 'core/Offers/utils'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import useNotification from 'hooks/useNotification'
import { usePaginationWithSearchParams } from 'hooks/usePagination'
import fullMoreIcon from 'icons/full-more.svg'
import { onSubmit as onRecurrenceSubmit } from 'screens/IndividualOffer/StocksEventCreation/form/onSubmit'
import { Button, DatePicker, Select, TextInput, TimePicker } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { BaseTimePicker } from 'ui-kit/form/TimePicker/BaseTimePicker'
import { getToday } from 'utils/date'
import { hasErrorCode } from 'utils/error'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import ActionBar from '../ActionBar/ActionBar'
import DialogStockEventDeleteConfirm from '../DialogStockDeleteConfirm/DialogStockEventDeleteConfirm'
import DialogStocksEventEditConfirm from '../DialogStocksEventEditConfirm/DialogStocksEventEditConfirm'
import useNotifyFormError from '../hooks/useNotifyFormError'
import { RecurrenceFormValues } from '../StocksEventCreation/form/types'
import { RecurrenceForm } from '../StocksEventCreation/RecurrenceForm'
import { getSuccessMessage } from '../utils/getSuccessMessage'

import { EventCancellationBanner } from './EventCancellationBanner'
import { getPriceCategoryOptions } from './getPriceCategoryOptions'
import { hasChangesOnStockWithBookings } from './hasChangesOnStockWithBookings'
import { STOCK_EVENT_FORM_DEFAULT_VALUES } from './StockFormList/constants'
import { StocksEventFormSortingColumn } from './StockFormList/stocksFiltering'
import {
  StockEventFormValues,
  StocksEventFormValues,
} from './StockFormList/types'
import { buildInitialValues } from './StockFormList/utils'
import { getValidationSchema } from './StockFormList/validationSchema'
import styles from './StocksEventEdition.module.scss'
import { submitToApi } from './submitToApi'

const getEditedStocks = (
  stocks: StockEventFormValues[],
  initialsStocks: StockEventFormValues[]
): StockEventFormValues[] => {
  return stocks.reduce<StockEventFormValues[]>((accumulator, stock) => {
    const initialStock = initialsStocks.find(
      (initialStock) => initialStock.stockId === stock.stockId
    )

    if (!isEqual(stock, initialStock)) {
      accumulator.push(stock)
    }

    return accumulator
  }, [])
}

const hasStocksChanged = (
  stocks: StockEventFormValues[],
  initialsStocks: StockEventFormValues[]
): boolean => {
  return stocks.some((stock) => {
    const initialStock = initialsStocks.find(
      (initialStock) => initialStock.stockId === stock.stockId
    )

    return !isEqual(stock, initialStock)
  })
}
export interface StocksEventEditionProps {
  offer: IndividualOffer
}

const StocksEventEdition = ({
  offer,
}: StocksEventEditionProps): JSX.Element => {
  // utilities
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const notify = useNotification()
  const [searchParams, setSearchParams] = useSearchParams()

  // states
  const [isStocksEventConfirmModal, setIsStocksEventConfirmModal] =
    useState(false)
  const [isDeleteStockConfirmModalOpen, setIsDeleteConfirmModalOpen] =
    useState(false)
  const [stocks, setStocks] = useState<StocksEvent[]>([])
  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)
  const [stocksCount, setStocksCount] = useState<number>(0)
  const [dateFilter, setDateFilter] = useState(searchParams.get('date'))
  const [timeFilter, setTimeFilter] = useState(searchParams.get('time'))
  const [priceCategoryIdFilter, setPriceCategoryIdFilter] = useState(
    searchParams.get('priceCategoryId')
  )
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<StocksEventFormSortingColumn>()
  const { page, previousPage, nextPage, pageCount, firstPage } =
    usePaginationWithSearchParams(STOCKS_PER_PAGE, stocksCount)

  const priceCategoriesOptions = getPriceCategoryOptions(offer.priceCategories)

  const onCancel = () => setIsRecurrenceModalOpen(false)
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departementCode
  )

  const resetStocks = (newStocks: StocksEvent[]) => {
    setStocks(newStocks)
    const stocksForForm = buildInitialValues({
      departementCode: offer.venue.departementCode,
      stocks: newStocks,
      today,
      lastProviderName: offer.lastProviderName,
      offerStatus: offer.status,
      priceCategoriesOptions,
    })
    formik.resetForm({
      values: stocksForForm,
    })
  }

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

    const allStockValues = [...values.stocks, ...hiddenStocksRef.current]
    const isFormEmpty = allStockValues.every((val) =>
      isEqual(val, STOCK_EVENT_FORM_DEFAULT_VALUES)
    )

    const editedStocks = getEditedStocks(allStockValues, initialValues.stocks)

    if (isFormEmpty || editedStocks.length === 0) {
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Show modal if there is changes on stock with bookings on some fields
    const changesOnStockWithBookings = hasChangesOnStockWithBookings(
      editedStocks,
      formik.initialValues.stocks
    )
    if (!isStocksEventConfirmModal && changesOnStockWithBookings) {
      setIsStocksEventConfirmModal(true)
      return
    }

    try {
      await submitToApi(
        editedStocks,
        offer.id,
        offer.venue.departementCode ?? '',
        formik.setErrors
      )
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error?.message)
      }
      return
    }

    navigate(nextStepUrl)
    notify.success(getSuccessMessage(mode))
    setIsStocksEventConfirmModal(false)
  }

  const handleRecurrenceSubmit = async (values: RecurrenceFormValues) => {
    const newStocks = await onRecurrenceSubmit(
      values,
      offer.venue.departementCode ?? '',
      offer.id,
      notify
    )
    if (newStocks?.length) {
      resetStocks(newStocks)
    }
    setIsRecurrenceModalOpen(false)
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

      // We also need to remove it from the stocks state
      // otherwise it will be re-rendered at next creation
      const removedStockIndex = stocks.findIndex(
        (stock) => stock.id === stockId
      )
      if (removedStockIndex > -1) {
        stocks.splice(removedStockIndex, 1)
        setStocks(stocks)
      }

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
    stocks,
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

  const isDisabled = isOfferDisabled(offer.status)
  const isSynchronized = Boolean(offer.lastProvider)
  const onFilterChange = () => {
    firstPage()
  }
  const areFiltersActive = Boolean(
    dateFilter || timeFilter || priceCategoryIdFilter
  )

  const computeMaxBookingLimitDatetime = (beginningDate: string) => {
    const [year, month, day] = beginningDate.split('-')

    return beginningDate !== ''
      ? new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
      : undefined
  }

  return (
    <FormikProvider value={formik}>
      {isStocksEventConfirmModal && (
        <DialogStocksEventEditConfirm
          onConfirm={formik.submitForm}
          onCancel={() => setIsStocksEventConfirmModal(false)}
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
                  priceCategories={offer.priceCategories ?? []}
                  setIsOpen={setIsRecurrenceModalOpen}
                  handleSubmit={handleRecurrenceSubmit}
                />
              </DialogBox>
            )}

            <FieldArray
              name="stocks"
              render={() => (
                <>
                  <table className={styles['stock-table']}>
                    <caption className="visually-hidden">
                      Tableau d'édition des stocks
                    </caption>

                    <thead
                      className={cn({
                        [styles['filters-active']]: areFiltersActive,
                      })}
                    >
                      <tr>
                        <th
                          className={cn(
                            styles['table-head'],
                            styles['head-date']
                          )}
                          scope="col"
                        >
                          <span className={styles['header-name']}>Date</span>

                          <SortArrow
                            onClick={() =>
                              onColumnHeaderClick(
                                StocksEventFormSortingColumn.DATE
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksEventFormSortingColumn.DATE
                                ? currentSortingMode
                                : SortingMode.NONE
                            }
                          />

                          <div className={cn(styles['filter-input'])}>
                            <BaseDatePicker
                              onChange={(event) => {
                                setDateFilter(event.target.value)
                                onFilterChange()
                              }}
                              value={dateFilter ?? ''}
                              filterVariant
                              aria-label="Filtrer par date"
                            />
                          </div>
                        </th>

                        <th
                          className={cn(
                            styles['table-head'],
                            styles['head-time']
                          )}
                          scope="col"
                        >
                          <span className={styles['header-name']}>Horaire</span>

                          <SortArrow
                            onClick={() =>
                              onColumnHeaderClick(
                                StocksEventFormSortingColumn.HOUR
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksEventFormSortingColumn.HOUR
                                ? currentSortingMode
                                : SortingMode.NONE
                            }
                          />
                          <div className={cn(styles['filter-input'])}>
                            <BaseTimePicker
                              onChange={(event) => {
                                setTimeFilter(event.target.value)
                                onFilterChange()
                              }}
                              value={timeFilter ?? ''}
                              filterVariant
                              aria-label="Filtrer par horaire"
                            />
                          </div>
                        </th>

                        <th
                          className={cn(
                            styles['table-head'],
                            styles['head-price']
                          )}
                          scope="col"
                        >
                          <span className={styles['header-name']}>Tarif</span>

                          <SortArrow
                            onClick={() =>
                              onColumnHeaderClick(
                                StocksEventFormSortingColumn.PRICE_CATEGORY
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksEventFormSortingColumn.PRICE_CATEGORY
                                ? currentSortingMode
                                : SortingMode.NONE
                            }
                          />
                          <div className={cn(styles['filter-input'])}>
                            <SelectInput
                              name="priceCategoryIdFilter"
                              defaultOption={{ label: '', value: '' }}
                              options={priceCategoriesOptions}
                              value={priceCategoryIdFilter ?? ''}
                              onChange={(event) => {
                                setPriceCategoryIdFilter(event.target.value)
                                onFilterChange()
                              }}
                              filterVariant
                              aria-label="Filtrer par tarif"
                            />
                          </div>
                        </th>

                        <th
                          className={cn(
                            styles['table-head'],
                            styles['head-booking-limit-datetime']
                          )}
                          scope="col"
                        >
                          <span className={styles['header-name']}>
                            Date limite
                            <br />
                            de réservation
                          </span>

                          <SortArrow
                            onClick={() =>
                              onColumnHeaderClick(
                                StocksEventFormSortingColumn.BOOKING_LIMIT_DATETIME
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksEventFormSortingColumn.BOOKING_LIMIT_DATETIME
                                ? currentSortingMode
                                : SortingMode.NONE
                            }
                          />
                          <div className={cn(styles['filter-input'])}>
                            &nbsp;
                          </div>
                        </th>

                        <th
                          className={cn(
                            styles['table-head'],
                            styles['head-remaining-quantity']
                          )}
                          scope="col"
                        >
                          <span className={styles['header-name']}>
                            Quantité restante
                          </span>

                          <SortArrow
                            onClick={() =>
                              onColumnHeaderClick(
                                StocksEventFormSortingColumn.REMAINING_QUANTITY
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksEventFormSortingColumn.REMAINING_QUANTITY
                                ? currentSortingMode
                                : SortingMode.NONE
                            }
                          />
                          <div className={cn(styles['filter-input'])}>
                            &nbsp;
                          </div>
                        </th>

                        <th
                          className={cn(
                            styles['table-head'],
                            styles['head-booking-quantity']
                          )}
                          scope="col"
                        >
                          <span className={styles['header-name']}>
                            Réservations
                          </span>

                          <SortArrow
                            onClick={() =>
                              onColumnHeaderClick(
                                StocksEventFormSortingColumn.BOOKINGS_QUANTITY
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksEventFormSortingColumn.BOOKINGS_QUANTITY
                                ? currentSortingMode
                                : SortingMode.NONE
                            }
                          />
                          <div className={cn(styles['filter-input'])}>
                            &nbsp;
                          </div>
                        </th>

                        <th className={styles['head-actions']}></th>
                      </tr>
                    </thead>

                    <tbody className={styles['table-body']}>
                      {areFiltersActive && (
                        <FilterResultsRow
                          colSpan={7}
                          onFiltersReset={() => {
                            setDateFilter('')
                            setTimeFilter('')
                            setPriceCategoryIdFilter('')
                            onFilterChange()
                          }}
                          resultsCount={values.stocks.length}
                        />
                      )}

                      {currentPageItems.map(
                        (stockValues: StockEventFormValues, indexInPage) => {
                          const index =
                            (page - 1) * STOCKS_PER_PAGE + indexInPage

                          const stockFormValues = values.stocks[index]

                          const { readOnlyFields } = stockFormValues

                          const beginningDate = stockFormValues.beginningDate
                          const actions = [
                            {
                              callback: async () => {
                                if (stockValues.bookingsQuantity > 0) {
                                  setDeletingStockData({
                                    deletingStock: stockValues,
                                    deletingIndex: index,
                                  })
                                  setIsDeleteConfirmModalOpen(true)
                                } else {
                                  /* istanbul ignore next: DEBT, TO FIX */
                                  await onDeleteStock(stockValues, index)
                                }
                              },
                              label: 'Supprimer le stock',
                              disabled: !stockValues.isDeletable || isDisabled,
                              icon: fullTrashIcon,
                            },
                          ]

                          return (
                            <tr className={styles['table-row']} key={index}>
                              <td className={styles['data']}>
                                <DatePicker
                                  smallLabel
                                  name={`stocks[${index}]beginningDate`}
                                  label="Date"
                                  isLabelHidden
                                  minDate={today}
                                  disabled={readOnlyFields.includes(
                                    'beginningDate'
                                  )}
                                  hideFooter
                                />
                              </td>

                              <td className={styles['data']}>
                                <TimePicker
                                  smallLabel
                                  label="Horaire"
                                  isLabelHidden
                                  name={`stocks[${index}]beginningTime`}
                                  disabled={readOnlyFields.includes(
                                    'beginningTime'
                                  )}
                                  hideFooter
                                />
                              </td>

                              <td className={styles['data']}>
                                <Select
                                  name={`stocks[${index}]priceCategoryId`}
                                  options={priceCategoriesOptions}
                                  smallLabel
                                  label="Tarif"
                                  isLabelHidden
                                  defaultOption={{
                                    label: 'Sélectionner un tarif',
                                    value: '',
                                  }}
                                  disabled={
                                    priceCategoriesOptions.length === 1 ||
                                    readOnlyFields.includes('priceCategoryId')
                                  }
                                  hideFooter
                                />
                              </td>

                              <td className={styles['data']}>
                                <DatePicker
                                  smallLabel
                                  name={`stocks[${index}]bookingLimitDatetime`}
                                  label="Date limite de réservation"
                                  isLabelHidden
                                  minDate={today}
                                  maxDate={computeMaxBookingLimitDatetime(
                                    beginningDate
                                  )}
                                  disabled={readOnlyFields.includes(
                                    'bookingLimitDatetime'
                                  )}
                                  hideFooter
                                />
                              </td>

                              <td className={styles['data']}>
                                <TextInput
                                  smallLabel
                                  name={`stocks[${index}]remainingQuantity`}
                                  label={
                                    mode === OFFER_WIZARD_MODE.EDITION
                                      ? 'Quantité restante'
                                      : 'Quantité'
                                  }
                                  isLabelHidden
                                  placeholder="Illimité"
                                  disabled={readOnlyFields.includes(
                                    'remainingQuantity'
                                  )}
                                  type="number"
                                  hasDecimal={false}
                                  hideFooter
                                />
                              </td>

                              <td className={styles['data']}>
                                <TextInput
                                  name={`stocks[${index}]bookingsQuantity`}
                                  value={
                                    values.stocks[index].bookingsQuantity || 0
                                  }
                                  readOnly
                                  label="Réservations"
                                  isLabelHidden
                                  smallLabel
                                  hideFooter
                                />
                              </td>

                              {actions && actions.length > 0 && (
                                <td className={styles['stock-actions']}>
                                  <StockFormActions
                                    actions={actions}
                                    disabled={false}
                                  />
                                </td>
                              )}
                            </tr>
                          )
                        }
                      )}

                      {values.stocks.length === 0 && (
                        <NoResultsRow colSpan={7} />
                      )}
                    </tbody>
                  </table>

                  <Pagination
                    currentPage={page}
                    pageCount={pageCount}
                    onPreviousPageClick={previousPage}
                    onNextPageClick={nextPage}
                  />

                  {isDeleteStockConfirmModalOpen && (
                    <DialogStockEventDeleteConfirm
                      /* istanbul ignore next: DEBT, TO FIX */
                      onConfirm={async () => {
                        /* istanbul ignore next: DEBT, TO FIX */
                        if (deletingStockData !== null) {
                          const { deletingStock, deletingIndex } =
                            deletingStockData
                          await onDeleteStock(deletingStock, deletingIndex)
                        }
                        setIsDeleteConfirmModalOpen(false)
                      }}
                      onCancel={() => setIsDeleteConfirmModalOpen(false)}
                    />
                  )}
                </>
              )}
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
