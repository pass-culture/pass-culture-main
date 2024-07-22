import cn from 'classnames'
import { FieldArray, FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash/isEqual'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  GetStocksResponseModel,
  StocksOrderedBy,
  OfferStatus,
} from 'apiClient/v1'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { DialogBox } from 'components/DialogBox/DialogBox'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { FilterResultsRow } from 'components/StocksEventList/FilterResultsRow'
import { NoResultsRow } from 'components/StocksEventList/NoResultsRow'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { STOCKS_PER_PAGE } from 'components/StocksEventList/StocksEventList'
import { GET_OFFER_QUERY_KEY } from 'config/swrQueryKeys'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'
import { SelectOption } from 'custom_types/form'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import { useNotification } from 'hooks/useNotification'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import { usePaginationWithSearchParams } from 'hooks/usePagination'
import fullMoreIcon from 'icons/full-more.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { onSubmit as onRecurrenceSubmit } from 'screens/IndividualOffer/StocksEventCreation/form/onSubmit'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { Select } from 'ui-kit/form/Select/Select'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { BaseTimePicker } from 'ui-kit/form/TimePicker/BaseTimePicker'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { getToday } from 'utils/date'
import { hasErrorCode } from 'utils/error'
import {
  convertTimeFromVenueTimezoneToUtc,
  getLocalDepartementDateTimeFromUtc,
} from 'utils/timezone'

import { ActionBar } from '../ActionBar/ActionBar'
import { DialogStockEventDeleteConfirm } from '../DialogStockDeleteConfirm/DialogStockEventDeleteConfirm'
import { DialogStocksEventEditConfirm } from '../DialogStocksEventEditConfirm/DialogStocksEventEditConfirm'
import { useNotifyFormError } from '../hooks/useNotifyFormError'
import { RecurrenceFormValues } from '../StocksEventCreation/form/types'
import { RecurrenceForm } from '../StocksEventCreation/RecurrenceForm'
import { getSuccessMessage } from '../utils/getSuccessMessage'

import { EventCancellationBanner } from './EventCancellationBanner'
import { getPriceCategoryOptions } from './getPriceCategoryOptions'
import { hasChangesOnStockWithBookings } from './hasChangesOnStockWithBookings'
import { StockEventFormActions } from './StockEventFormActions/StockEventFormActions'
import { STOCK_EVENT_FORM_DEFAULT_VALUES } from './StockFormList/constants'
import {
  StockEventFormValues,
  StocksEventFormValues,
} from './StockFormList/types'
import { buildInitialValues } from './StockFormList/utils/buildInitialValues'
import { getValidationSchema } from './StockFormList/validationSchema'
import styles from './StocksEventEdition.module.scss'
import { submitToApi } from './submitToApi'

const computeMaxBookingLimitDatetime = (beginningDate: string) => {
  const [year, month, day] = beginningDate.split('-')

  return beginningDate !== ''
    ? new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
    : undefined
}

type ResetFormWithNewPage = {
  response: GetStocksResponseModel
  setInitialValues: (values: StocksEventFormValues) => void
  setStocksCount: (count: number) => void
  today: Date
  lastProviderName: string | null
  offerStatus: OfferStatus
  priceCategoriesOptions: SelectOption[]
  departmentCode?: string | null
}

function resetFormWithNewPage({
  response,
  setInitialValues,
  setStocksCount,
  today,
  lastProviderName,
  offerStatus,
  priceCategoriesOptions,
  departmentCode,
}: ResetFormWithNewPage) {
  setInitialValues(
    buildInitialValues({
      departementCode: departmentCode,
      stocks: response.stocks,
      today,
      lastProviderName,
      offerStatus,
      priceCategoriesOptions,
    })
  )
  setStocksCount(response.stockCount)
}

interface StocksEventEditionProps {
  offer: GetIndividualOfferResponseModel
}

export const StocksEventEdition = ({
  offer,
}: StocksEventEditionProps): JSX.Element => {
  // utilities
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { mutate } = useSWRConfig()
  const notify = useNotification()
  const [searchParams, setSearchParams] = useSearchParams()
  const priceCategoriesOptions = useMemo(
    () => getPriceCategoryOptions(offer.priceCategories),
    [offer.priceCategories]
  )
  const today = useMemo(
    () =>
      getLocalDepartementDateTimeFromUtc(
        getToday(),
        offer.venue.departementCode
      ),
    [offer.venue.departementCode]
  )

  // states
  const [isStocksEventConfirmModal, setIsStocksEventConfirmModal] =
    useState(false)
  const [stockToDeleteWithConfirmation, setStockToDeleteWithConfirmation] =
    useState<StockEventFormValues | null>(null)
  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)
  const [stocksCount, setStocksCount] = useState<number | null>(null)
  const [dateFilter, setDateFilter] = useState(searchParams.get('date'))
  const [timeFilter, setTimeFilter] = useState(searchParams.get('time'))
  const [priceCategoryIdFilter, setPriceCategoryIdFilter] = useState(
    searchParams.get('priceCategoryId')
  )
  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<StocksOrderedBy>()
  const { page, previousPage, nextPage, pageCount, firstPage } =
    usePaginationWithSearchParams(STOCKS_PER_PAGE, stocksCount ?? 0)
  const [initialValues, setInitialValues] = useState<StocksEventFormValues>({
    stocks: [],
  })
  const [
    shouldBlockNextPageNavigationFormIsDirty,
    setShouldBlockNextPageNavigationFormIsDirty,
  ] = useState(false)
  const [
    shouldBlockPreviousPageNavigationFormIsDirty,
    setShouldBlockPreviousPageNavigationFormIsDirty,
  ] = useState(false)

  const loadStocksFromCurrentFilters = useCallback(
    () =>
      api.getStocks(
        offer.id,
        dateFilter ? dateFilter : undefined,
        timeFilter
          ? convertTimeFromVenueTimezoneToUtc(
              timeFilter,
              offer.venue.departementCode
            )
          : undefined,
        priceCategoryIdFilter ? Number(priceCategoryIdFilter) : undefined,
        currentSortingColumn ?? undefined,
        currentSortingMode === SortingMode.DESC,
        Number(page || 1)
      ),
    [
      currentSortingColumn,
      dateFilter,
      offer.id,
      offer.venue.departementCode,
      page,
      priceCategoryIdFilter,
      currentSortingMode,
      timeFilter,
    ]
  )

  // Effect
  useEffect(() => {
    if (dateFilter) {
      searchParams.set('date', dateFilter)
    } else {
      searchParams.delete('date')
    }
    if (timeFilter) {
      searchParams.set('time', timeFilter)
    } else {
      searchParams.delete('time')
    }
    if (priceCategoryIdFilter) {
      searchParams.set('priceCategoryId', priceCategoryIdFilter)
    } else {
      searchParams.delete('priceCategoryId')
    }
    if (currentSortingColumn) {
      searchParams.set('orderBy', currentSortingColumn)
    } else {
      searchParams.delete('orderBy')
    }
    if (currentSortingMode === SortingMode.DESC) {
      searchParams.set('orderByDesc', '1')
    } else if (currentSortingMode === SortingMode.ASC) {
      searchParams.set('orderByDesc', '0')
    } else {
      searchParams.delete('orderByDesc')
    }

    setSearchParams(searchParams)

    async function loadStocks() {
      const response = await loadStocksFromCurrentFilters()

      if (!ignore) {
        resetFormWithNewPage({
          response,
          setInitialValues,
          setStocksCount,
          today,
          lastProviderName: offer.lastProvider?.name ?? null,
          offerStatus: offer.status,
          priceCategoriesOptions,
          departmentCode: offer.venue.departementCode,
        })
      }
    }

    // we set ignore variable to avoid race conditions
    // see react doc:  https://react.dev/reference/react/useEffect#fetching-data-with-effects
    let ignore = false

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadStocks()
    return () => {
      ignore = true
    }
  }, [
    dateFilter,
    timeFilter,
    priceCategoryIdFilter,
    currentSortingColumn,
    currentSortingMode,
    page,
    loadStocksFromCurrentFilters,
    searchParams,
    setSearchParams,
    offer.lastProvider?.name,
    offer.status,
    priceCategoriesOptions,
    today,
    offer.venue.departementCode,
  ])

  const onCancel = () => setIsRecurrenceModalOpen(false)

  const onSubmit = async (values: StocksEventFormValues) => {
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step: OFFER_WIZARD_STEP_IDS.STOCKS,
      mode: OFFER_WIZARD_MODE.READ_ONLY,
    })

    const isFormEmpty = values.stocks.every((val) =>
      isEqual(val, STOCK_EVENT_FORM_DEFAULT_VALUES)
    )

    if (isFormEmpty || !formik.dirty) {
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Show modal if there is changes on stock with bookings on some fields
    const changesOnStockWithBookings = hasChangesOnStockWithBookings(
      values.stocks,
      formik.initialValues.stocks
    )
    if (!isStocksEventConfirmModal && changesOnStockWithBookings) {
      setIsStocksEventConfirmModal(true)
      return
    }

    try {
      await submitToApi(
        values.stocks,
        offer.id,
        offer.venue.departementCode ?? ''
      )
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error.message)
      }
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offer.id])
    navigate(nextStepUrl)
    notify.success(getSuccessMessage(mode))
    setIsStocksEventConfirmModal(false)
  }

  const handleRecurrenceSubmit = async (values: RecurrenceFormValues) => {
    await onRecurrenceSubmit(
      values,
      offer.venue.departementCode ?? '',
      offer.id,
      notify
    )
    const response = await loadStocksFromCurrentFilters()
    resetFormWithNewPage({
      response,
      setInitialValues,
      setStocksCount,
      today,
      lastProviderName: offer.lastProvider?.name ?? null,
      offerStatus: offer.status,
      priceCategoriesOptions,
      departmentCode: offer.venue.departementCode,
    })
    setIsRecurrenceModalOpen(false)
  }

  const onDeleteStock = async (stock: StockEventFormValues) => {
    const { isDeletable, stockId } = stock
    if (!isDeletable) {
      return
    }

    try {
      await api.deleteStock(stockId)

      const newStocks = formik.values.stocks.filter(
        (initialStock) => initialStock.stockId !== stockId
      )

      if (newStocks.length > 0) {
        formik.resetForm({ values: { stocks: newStocks } })
      } else {
        if (page === pageCount && page !== 1) {
          previousPage()
        } else {
          // Reload this current page
          const response = await loadStocksFromCurrentFilters()
          resetFormWithNewPage({
            response,
            setInitialValues,
            setStocksCount,
            today,
            lastProviderName: offer.lastProvider?.name ?? null,
            offerStatus: offer.status,
            priceCategoriesOptions,
            departmentCode: offer.venue.departementCode,
          })
        }
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

  const formik = useFormik<StocksEventFormValues>({
    initialValues,
    onSubmit,
    validationSchema: () => getValidationSchema(priceCategoriesOptions),
    enableReinitialize: true,
  })

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

  const onFilterChange = () => {
    firstPage()
  }
  const isDisabled = isOfferDisabled(offer.status)
  const isSynchronized = Boolean(offer.lastProvider)
  const areFiltersActive = Boolean(
    dateFilter || timeFilter || priceCategoryIdFilter
  )

  function resetPageNavigationBlockers() {
    setShouldBlockNextPageNavigationFormIsDirty(false)
    setShouldBlockPreviousPageNavigationFormIsDirty(false)
  }

  if (stocksCount === null) {
    return <Spinner />
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
                  idLabelledBy="add-recurrence"
                />
              </DialogBox>
            )}

            <FieldArray
              name="stocks"
              render={() => (
                <div className={styles['stock-table-container']}>
                  <table className={styles['stock-table']}>
                    <caption className="visually-hidden">
                      Tableau d’édition des stocks
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
                              onColumnHeaderClick(StocksOrderedBy.DATE)
                            }
                            sortingMode={
                              currentSortingColumn === StocksOrderedBy.DATE
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
                              onColumnHeaderClick(StocksOrderedBy.TIME)
                            }
                            sortingMode={
                              currentSortingColumn === StocksOrderedBy.TIME
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
                                StocksOrderedBy.PRICE_CATEGORY_ID
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksOrderedBy.PRICE_CATEGORY_ID
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
                                StocksOrderedBy.BOOKING_LIMIT_DATETIME
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksOrderedBy.BOOKING_LIMIT_DATETIME
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
                                StocksOrderedBy.REMAINING_QUANTITY
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksOrderedBy.REMAINING_QUANTITY
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
                                StocksOrderedBy.DN_BOOKED_QUANTITY
                              )
                            }
                            sortingMode={
                              currentSortingColumn ===
                              StocksOrderedBy.DN_BOOKED_QUANTITY
                                ? currentSortingMode
                                : SortingMode.NONE
                            }
                          />
                          <div className={cn(styles['filter-input'])}>
                            &nbsp;
                          </div>
                        </th>

                        <th className={styles['head-actions']} />
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
                        />
                      )}

                      {formik.values.stocks.map((stock, index) => {
                        const { readOnlyFields } = stock

                        const beginningDate = stock.beginningDate
                        const actions = [
                          {
                            callback: async () => {
                              if (stock.bookingsQuantity > 0) {
                                setStockToDeleteWithConfirmation(stock)
                              } else {
                                await onDeleteStock(stock)
                              }
                            },
                            label: 'Supprimer le stock',
                            disabled: !stock.isDeletable || isDisabled,
                            icon: fullTrashIcon,
                          },
                        ]

                        return (
                          <tr
                            className={styles['table-row']}
                            key={stock.stockId}
                          >
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
                                  formik.values.stocks[index].bookingsQuantity
                                }
                                readOnly
                                label="Réservations"
                                isLabelHidden
                                smallLabel
                                hideFooter
                              />
                            </td>

                            {actions.length > 0 && (
                              <td className={styles['stock-actions']}>
                                <StockEventFormActions actions={actions} />
                              </td>
                            )}
                          </tr>
                        )
                      })}

                      {formik.values.stocks.length === 0 && (
                        <NoResultsRow colSpan={7} />
                      )}
                    </tbody>
                  </table>

                  <Pagination
                    currentPage={page}
                    pageCount={pageCount}
                    onPreviousPageClick={() => {
                      if (formik.dirty) {
                        setShouldBlockPreviousPageNavigationFormIsDirty(true)
                        return
                      }
                      previousPage()
                    }}
                    onNextPageClick={() => {
                      if (formik.dirty) {
                        setShouldBlockNextPageNavigationFormIsDirty(true)
                        return
                      }
                      nextPage()
                    }}
                  />

                  {stockToDeleteWithConfirmation !== null && (
                    <DialogStockEventDeleteConfirm
                      onConfirm={async () => {
                        await onDeleteStock(stockToDeleteWithConfirmation)
                        setStockToDeleteWithConfirmation(null)
                      }}
                      onCancel={() => setStockToDeleteWithConfirmation(null)}
                    />
                  )}
                </div>
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
        when={formik.dirty && !formik.isSubmitting}
      />
      {(shouldBlockNextPageNavigationFormIsDirty ||
        shouldBlockPreviousPageNavigationFormIsDirty) && (
        <ConfirmDialog
          onCancel={resetPageNavigationBlockers}
          leftButtonAction={() => {
            resetPageNavigationBlockers()
            if (shouldBlockPreviousPageNavigationFormIsDirty) {
              previousPage()
            } else {
              nextPage()
            }
          }}
          onConfirm={resetPageNavigationBlockers}
          title="Les informations non enregistrées seront perdues"
          confirmText="Rester sur la page"
          cancelText="Quitter la page"
        />
      )}
    </FormikProvider>
  )
}
