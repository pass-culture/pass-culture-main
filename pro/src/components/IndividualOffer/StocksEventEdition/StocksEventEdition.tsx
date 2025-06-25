import { yupResolver } from '@hookform/resolvers/yup'
import cn from 'classnames'
import { format } from 'date-fns'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useFieldArray, useForm, UseFormSetValue } from 'react-hook-form'
import { useLocation, useNavigate, useSearchParams } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  GetStocksResponseModel,
  OfferStatus,
  StocksOrderedBy,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { SelectOption } from 'commons/custom_types/form'
import { SortingMode, useColumnSorting } from 'commons/hooks/useColumnSorting'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferWizardMode } from 'commons/hooks/useOfferWizardMode'
import { usePaginationWithSearchParams } from 'commons/hooks/usePagination'
import { FORMAT_ISO_DATE_ONLY, getToday } from 'commons/utils/date'
import { hasErrorCode } from 'commons/utils/error'
import { isEqual } from 'commons/utils/isEqual'
import {
  convertTimeFromVenueTimezoneToUtc,
  getLocalDepartementDateTimeFromUtc,
  isValidTime,
} from 'commons/utils/timezone'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { onSubmit as onRecurrenceSubmit } from 'components/IndividualOffer/StocksEventCreation/form/onSubmit'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { RouteLeavingGuardIndividualOffer } from 'components/RouteLeavingGuardIndividualOffer/RouteLeavingGuardIndividualOffer'
import { NoResultsRow } from 'components/StocksEventList/NoResultsRow'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { STOCKS_PER_PAGE } from 'components/StocksEventList/StocksEventList'
import fullMoreIcon from 'icons/full-more.svg'
import fullRefreshIcon from 'icons/full-refresh.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import { ActionBar } from 'pages/IndividualOffer/components/ActionBar/ActionBar'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { QuantityInput } from 'ui-kit/formV2/QuantityInput/QuantityInput'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TimePicker } from 'ui-kit/formV2/TimePicker/TimePicker'
import { Pagination } from 'ui-kit/Pagination/Pagination'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import { DialogStockEventDeleteConfirm } from '../DialogStockDeleteConfirm/DialogStockEventDeleteConfirm'
import { DialogStocksEventEditConfirm } from '../DialogStocksEventEditConfirm/DialogStocksEventEditConfirm'
import { RecurrenceFormValues } from '../StocksEventCreation/form/types'
import { RecurrenceForm } from '../StocksEventCreation/RecurrenceForm'
import { getDepartmentCode } from '../utils/getDepartmentCode'
import { getSuccessMessage } from '../utils/getSuccessMessage'

import { EventCancellationBanner } from './EventCancellationBanner'
import { getPriceCategoryOptions } from './getPriceCategoryOptions'
import { hasChangesOnStockWithBookings } from './hasChangesOnStockWithBookings'
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
  setValue: UseFormSetValue<StocksEventFormValues>
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
  setValue,
  setStocksCount,
  today,
  lastProviderName,
  offerStatus,
  priceCategoriesOptions,
  departmentCode,
}: ResetFormWithNewPage) {
  const values = buildInitialValues({
    departementCode: departmentCode,
    stocks: response.stocks,
    today,
    lastProviderName,
    offerStatus,
    priceCategoriesOptions,
  })
  setInitialValues(values)
  setValue('stocks', values.stocks, { shouldDirty: false })
  setStocksCount(response.stockCount)
}

interface StocksEventEditionProps {
  offer: GetIndividualOfferWithAddressResponseModel
}

export const StocksEventEdition = ({
  offer,
}: StocksEventEditionProps): JSX.Element => {
  // utilities
  const { logEvent } = useAnalytics()
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const { mutate } = useSWRConfig()
  const notify = useNotification()
  const [searchParams, setSearchParams] = useSearchParams()
  const priceCategoriesOptions = useMemo(
    () => getPriceCategoryOptions(offer.priceCategories),
    [offer.priceCategories]
  )
  const departmentCode = getDepartmentCode(offer)

  const today = useMemo(
    () => getLocalDepartementDateTimeFromUtc(getToday(), departmentCode),
    [departmentCode]
  )

  // states
  const [isStocksEventConfirmModal, setIsStocksEventConfirmModal] =
    useState(false)
  const [stockToDeleteWithConfirmation, setStockToDeleteWithConfirmation] =
    useState<StockEventFormValues | null>(null)
  const [isRecurrenceModalOpen, setIsRecurrenceModalOpen] = useState(false)
  const [stocksCount, setStocksCount] = useState<number | null>(null)
  const [dateFilter, setDateFilter] = useState(searchParams.get('date'))
  const [timeFilter, setTimeFilter] = useState<string>(
    searchParams.get('time') || ''
  )
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

  function sortTableColumn(col: StocksOrderedBy) {
    logEvent(Events.CLICKED_SORT_STOCKS_TABLE, {
      formType: 'edition',
      sortBy: col,
      offerId: offer.id,
      venueId: offer.venue.id,
    })
    onColumnHeaderClick(col)
  }

  const loadStocksFromCurrentFilters = useCallback(
    () =>
      api.getStocks(
        offer.id,
        dateFilter ? dateFilter : undefined,
        isValidTime(timeFilter)
          ? convertTimeFromVenueTimezoneToUtc(timeFilter, departmentCode)
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
      departmentCode,
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
          setValue,
          setStocksCount,
          today,
          lastProviderName: offer.lastProvider?.name ?? null,
          offerStatus: offer.status,
          priceCategoriesOptions,
          departmentCode,
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
    departmentCode,
  ])

  const onSubmit = async (values: StocksEventFormValues) => {
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step: OFFER_WIZARD_STEP_IDS.STOCKS,
      mode: OFFER_WIZARD_MODE.READ_ONLY,
      isOnboarding,
    })

    const isFormEmpty = values.stocks.every((val) =>
      isEqual(val, STOCK_EVENT_FORM_DEFAULT_VALUES)
    )
    if (isFormEmpty || !isDirty) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      navigate(nextStepUrl)
      notify.success(getSuccessMessage(mode))
      return
    }

    // Show modal if there is changes on stock with bookings on some fields
    const changesOnStockWithBookings = hasChangesOnStockWithBookings(
      watch('stocks'),
      initialValues.stocks
    )
    if (!isStocksEventConfirmModal && changesOnStockWithBookings) {
      setIsStocksEventConfirmModal(true)
      return
    }

    try {
      await submitToApi(watch('stocks'), offer.id, departmentCode)
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error.message)
      }
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offer.id])
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(nextStepUrl)
    notify.success(getSuccessMessage(mode))
    setIsStocksEventConfirmModal(false)
  }

  const handleRecurrenceSubmit = async (values: RecurrenceFormValues) => {
    await onRecurrenceSubmit(values, departmentCode, offer.id, notify)
    const response = await loadStocksFromCurrentFilters()
    resetFormWithNewPage({
      response,
      setInitialValues,
      setValue,
      setStocksCount,
      today,
      lastProviderName: offer.lastProvider?.name ?? null,
      offerStatus: offer.status,
      priceCategoriesOptions,
      departmentCode,
    })

    // Always reload the offer to get the updated status.
    await mutate([GET_OFFER_QUERY_KEY, offer.id])

    setIsRecurrenceModalOpen(false)
  }

  const onDeleteStock = async (stock: StockEventFormValues) => {
    const { isDeletable, stockId } = stock
    if (!isDeletable && !stockId) {
      return
    }

    try {
      await api.deleteStock(stockId)

      const newStocks = initialValues.stocks.filter(
        (initialStock) => initialStock.stockId !== stockId
      )
      setInitialValues({
        stocks: newStocks,
      })
      setValue('stocks', newStocks, { shouldDirty: false })

      if (newStocks.length === 0) {
        if (page === pageCount && page !== 1) {
          previousPage()
        } else {
          // Reload this current page
          const response = await loadStocksFromCurrentFilters()
          resetFormWithNewPage({
            response,
            setInitialValues,
            setValue,
            setStocksCount,
            today,
            lastProviderName: offer.lastProvider?.name ?? null,
            offerStatus: offer.status,
            priceCategoriesOptions,
            departmentCode,
          })
        }
      }

      // Always reload the offer to get the updated status.
      await mutate([GET_OFFER_QUERY_KEY, offer.id])
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

  const hookForm = useForm<StocksEventFormValues, any, StocksEventFormValues>({
    resolver: yupResolver(getValidationSchema(priceCategoriesOptions)),
    defaultValues: initialValues,
    mode: 'onBlur',
  })

  const {
    register,
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting, isDirty },
  } = hookForm

  const { fields } = useFieldArray({
    control,
    name: 'stocks',
  })

  const handleBackToReadOnly = () => {
    /* istanbul ignore next: DEBT, TO FIX */
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode: OFFER_WIZARD_MODE.READ_ONLY,
        isOnboarding,
      })
    )
  }

  const onFilterChange = () => {
    firstPage()
    logEvent(Events.UPDATED_EVENT_STOCK_FILTERS, {
      formType: 'edition',
    })
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
    <>
      <DialogStocksEventEditConfirm
        onConfirm={handleSubmit(onSubmit)}
        onCancel={() => setIsStocksEventConfirmModal(false)}
        isDialogOpen={isStocksEventConfirmModal}
      />

      <FormLayout>
        <div aria-current="page">
          <form
            onSubmit={handleSubmit(onSubmit)}
            data-testid="stock-event-form"
          >
            <EventCancellationBanner offer={offer} />
            <div className={styles['add-dates-button']}>
              <DialogBuilder
                onOpenChange={setIsRecurrenceModalOpen}
                open={isRecurrenceModalOpen}
                variant="drawer"
                title="Ajouter une ou plusieurs dates"
                trigger={
                  <Button
                    variant={ButtonVariant.PRIMARY}
                    icon={fullMoreIcon}
                    disabled={isSynchronized || isDisabled}
                  >
                    Ajouter une ou plusieurs dates
                  </Button>
                }
              >
                <RecurrenceForm
                  priceCategories={offer.priceCategories ?? []}
                  handleSubmit={handleRecurrenceSubmit}
                />
              </DialogBuilder>
            </div>

            <div className={cn(styles['filter-input'])}>
              <div>
                <DatePicker
                  label="Filtrer par date"
                  name="dateFilter"
                  onChange={(event) => {
                    setDateFilter(event.target.value)
                    onFilterChange()
                  }}
                  value={dateFilter ?? ''}
                />
              </div>
              <div>
                <TimePicker
                  label="Filtrer par horaire"
                  name="timeFilter"
                  onChange={(event) => {
                    setTimeFilter(event.target.value)
                    onFilterChange()
                  }}
                  value={timeFilter}
                />
              </div>
              <div>
                <Select
                  label="Filtrer par tarif"
                  name="priceCategoryIdFilter"
                  defaultOption={{ label: '', value: '' }}
                  options={priceCategoriesOptions}
                  value={priceCategoryIdFilter ?? ''}
                  onChange={(event) => {
                    setPriceCategoryIdFilter(event.target.value)
                    onFilterChange()
                  }}
                />
              </div>
            </div>

            <Button
              icon={fullRefreshIcon}
              variant={ButtonVariant.TERNARY}
              onClick={() => {
                setDateFilter('')
                setTimeFilter('')
                setPriceCategoryIdFilter('')
                onFilterChange()
              }}
              disabled={!areFiltersActive}
            >
              Réinitialiser les filtres
            </Button>

            <div className={styles['stock-table-container']}>
              <table className={styles['stock-table']}>
                <caption className={styles['visually-hidden']}>
                  Tableau d’édition des stocks
                </caption>

                <thead>
                  <tr>
                    <th
                      className={cn(styles['table-head'], styles['head-date'])}
                      scope="col"
                    >
                      <span className={styles['header-name']}>Date</span>

                      <SortArrow
                        onClick={() => sortTableColumn(StocksOrderedBy.DATE)}
                        sortingMode={
                          currentSortingColumn === StocksOrderedBy.DATE
                            ? currentSortingMode
                            : SortingMode.NONE
                        }
                      />
                    </th>

                    <th
                      className={cn(styles['table-head'], styles['head-time'])}
                      scope="col"
                    >
                      <span className={styles['header-name']}>Horaire</span>

                      <SortArrow
                        onClick={() => sortTableColumn(StocksOrderedBy.TIME)}
                        sortingMode={
                          currentSortingColumn === StocksOrderedBy.TIME
                            ? currentSortingMode
                            : SortingMode.NONE
                        }
                      />
                    </th>

                    <th
                      className={cn(styles['table-head'], styles['head-price'])}
                      scope="col"
                    >
                      <span className={styles['header-name']}>Tarif</span>

                      <SortArrow
                        onClick={() =>
                          sortTableColumn(StocksOrderedBy.PRICE_CATEGORY_ID)
                        }
                        sortingMode={
                          currentSortingColumn ===
                          StocksOrderedBy.PRICE_CATEGORY_ID
                            ? currentSortingMode
                            : SortingMode.NONE
                        }
                      />
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
                          sortTableColumn(
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
                          sortTableColumn(StocksOrderedBy.REMAINING_QUANTITY)
                        }
                        sortingMode={
                          currentSortingColumn ===
                          StocksOrderedBy.REMAINING_QUANTITY
                            ? currentSortingMode
                            : SortingMode.NONE
                        }
                      />
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
                          sortTableColumn(StocksOrderedBy.DN_BOOKED_QUANTITY)
                        }
                        sortingMode={
                          currentSortingColumn ===
                          StocksOrderedBy.DN_BOOKED_QUANTITY
                            ? currentSortingMode
                            : SortingMode.NONE
                        }
                      />
                    </th>

                    <th className={styles['head-actions']} />
                  </tr>
                </thead>

                <tbody className={styles['table-body']}>
                  {fields.map((f, index) => {
                    const stock = f as unknown as StockEventFormValues
                    const { readOnlyFields } = stock

                    const beginningDate = stock.beginningDate

                    return (
                      <tr className={styles['table-row']} key={index}>
                        <td className={styles['data']}>
                          <DatePicker
                            label=""
                            {...register(`stocks.${index}.beginningDate`)}
                            error={
                              errors.stocks?.[index]?.beginningDate?.message
                            }
                            minDate={today}
                            disabled={readOnlyFields.includes('beginningDate')}
                          />
                        </td>

                        <td className={styles['data']}>
                          <TimePicker
                            {...register(`stocks.${index}.beginningTime`)}
                            error={
                              errors.stocks?.[index]?.beginningTime?.message
                            }
                            disabled={readOnlyFields.includes('beginningTime')}
                          />
                        </td>

                        <td className={styles['data']}>
                          <Select
                            label=""
                            {...register(`stocks.${index}.priceCategoryId`)}
                            error={
                              errors.stocks?.[index]?.priceCategoryId?.message
                            }
                            ariaLabel="Tarif"
                            options={priceCategoriesOptions}
                            defaultOption={{
                              label: 'Sélectionner un tarif',
                              value: '',
                            }}
                            disabled={
                              priceCategoriesOptions.length === 1 ||
                              readOnlyFields.includes('priceCategoryId')
                            }
                          />
                        </td>

                        <td className={styles['data']}>
                          <DatePicker
                            label=""
                            {...register(
                              `stocks.${index}.bookingLimitDatetime`
                            )}
                            error={
                              errors.stocks?.[index]?.bookingLimitDatetime
                                ?.message
                            }
                            minDate={today}
                            maxDate={
                              beginningDate
                                ? computeMaxBookingLimitDatetime(
                                    format(beginningDate, FORMAT_ISO_DATE_ONLY)
                                  )
                                : undefined
                            }
                            disabled={readOnlyFields.includes(
                              'bookingLimitDatetime'
                            )}
                          />
                        </td>

                        <td className={styles['data']}>
                          <QuantityInput
                            className={styles['quantity-input']}
                            minimum={0}
                            error={
                              errors.stocks?.[index]?.remainingQuantity?.message
                            }
                            disabled={readOnlyFields.includes(
                              'remainingQuantity'
                            )}
                            label=""
                            value={
                              watch('stocks')[index].remainingQuantity ??
                              undefined
                            }
                            onChange={(event) =>
                              setValue(
                                `stocks.${index}.remainingQuantity`,
                                Number(event.target.value),
                                { shouldDirty: true }
                              )
                            }
                            ariaLabel="Quantité restante"
                          />
                        </td>

                        <td
                          align="center"
                          className={cn(
                            styles['data'],
                            styles['style-bookings-quantity']
                          )}
                        >
                          {watch('stocks')[index]?.bookingsQuantity}
                        </td>

                        {stock.isDeletable && !isDisabled && (
                          <td data-label="Supprimer" className={styles['data']}>
                            <Button
                              variant={ButtonVariant.TERNARY}
                              onClick={async () => {
                                if (stock.bookingsQuantity > 0) {
                                  setStockToDeleteWithConfirmation(stock)
                                } else {
                                  await onDeleteStock(stock)
                                }
                              }}
                              icon={fullTrashIcon}
                              tooltipContent={<>Supprimer</>}
                            />
                          </td>
                        )}
                      </tr>
                    )
                  })}
                  {fields.length === 0 && <NoResultsRow colSpan={7} />}
                </tbody>
              </table>

              <Pagination
                currentPage={page}
                pageCount={pageCount}
                onPreviousPageClick={() => {
                  if (isDirty) {
                    setShouldBlockPreviousPageNavigationFormIsDirty(true)
                    return
                  }
                  previousPage()
                }}
                onNextPageClick={() => {
                  if (isDirty) {
                    setShouldBlockNextPageNavigationFormIsDirty(true)
                    return
                  }
                  nextPage()
                }}
              />

              <DialogStockEventDeleteConfirm
                onConfirm={async () => {
                  if (!stockToDeleteWithConfirmation) {
                    return
                  }
                  await onDeleteStock(stockToDeleteWithConfirmation)
                  setStockToDeleteWithConfirmation(null)
                }}
                onCancel={() => setStockToDeleteWithConfirmation(null)}
                isDialogOpen={stockToDeleteWithConfirmation !== null}
              />
            </div>

            <ActionBar
              isDisabled={isSubmitting || isOfferDisabled(offer.status)}
              onClickPrevious={handleBackToReadOnly}
              step={OFFER_WIZARD_STEP_IDS.STOCKS}
            />
          </form>
        </div>
      </FormLayout>

      <RouteLeavingGuardIndividualOffer when={isDirty && !isSubmitting} />
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
        open={
          shouldBlockNextPageNavigationFormIsDirty ||
          shouldBlockPreviousPageNavigationFormIsDirty
        }
      />
    </>
  )
}
