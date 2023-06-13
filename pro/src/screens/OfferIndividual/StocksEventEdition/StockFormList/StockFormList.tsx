import cn from 'classnames'
import { isAfter } from 'date-fns'
import { FieldArray, useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { StockFormActions } from 'components/StockFormActions'
import { FilterResultsRow } from 'components/StocksEventList/FilterResultsRow'
import { NoResultsRow } from 'components/StocksEventList/NoResultsRow'
import { SortArrow } from 'components/StocksEventList/SortArrow'
import { isOfferDisabled, OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { SelectOption } from 'custom_types/form'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import { SortingMode, useColumnSorting } from 'hooks/useColumnSorting'
import { useModal } from 'hooks/useModal'
import { usePagination } from 'hooks/usePagination'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import DialogStockEventDeleteConfirm from 'screens/OfferIndividual/DialogStockDeleteConfirm/DialogStockEventDeleteConfirm'
import { DatePicker, Select, TextInput, TimePicker } from 'ui-kit'
import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { BaseTimePicker } from 'ui-kit/form/TimePicker/BaseTimePicker'
import { Pagination } from 'ui-kit/Pagination'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { STOCK_EVENT_EDITION_EMPTY_SYNCHRONIZED_READ_ONLY_FIELDS } from './constants'
import styles from './StockFormList.module.scss'
import {
  filterAndSortStocks,
  StocksEventFormSortingColumn,
} from './stocksFiltering'

import { StockEventFormValues, STOCK_EVENT_FORM_DEFAULT_VALUES } from './'

interface StockFormListProps {
  offer: IOfferIndividual
  onDeleteStock: (
    stockValues: StockEventFormValues,
    index: number
  ) => Promise<void>
  priceCategoriesOptions: SelectOption[]
  hiddenStocksRef: React.MutableRefObject<StockEventFormValues[]>
}

const STOCKS_PER_PAGE = 20

const StockFormList = ({
  offer,
  onDeleteStock,
  priceCategoriesOptions,
  hiddenStocksRef,
}: StockFormListProps) => {
  const {
    visible: deleteConfirmVisible,
    showModal: deleteConfirmShow,
    hideModal: deleteConfirmHide,
  } = useModal()
  const mode = useOfferWizardMode()
  const [deletingStockData, setDeletingStockData] = useState<{
    deletingStock: StockEventFormValues
    deletingIndex: number
  } | null>(null)
  const { values, setFieldValue, setTouched } = useFormikContext<{
    stocks: StockEventFormValues[]
  }>()
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departmentCode
  )
  const areFiltersEnabled = useActiveFeature('WIP_RECURRENCE_FILTERS')

  const { currentSortingColumn, currentSortingMode, onColumnHeaderClick } =
    useColumnSorting<StocksEventFormSortingColumn>()
  const [dateFilter, setDateFilter] = useState<Date | null>(null)
  const [hourFilter, setHourFilter] = useState<Date | null>(null)
  const [priceCategoryFilter, setPriceCategoryFilter] = useState('')
  const onFilterChange = () => {
    setPage(1)
  }
  const areFiltersActive = Boolean(
    dateFilter || hourFilter || priceCategoryFilter
  )

  useEffect(() => {
    const allStocks = [...values.stocks, ...hiddenStocksRef.current]
    const filteredStocks = filterAndSortStocks(
      allStocks,
      offer.priceCategories ?? [],
      currentSortingColumn,
      currentSortingMode,
      { dateFilter, hourFilter, priceCategoryFilter }
    )
    hiddenStocksRef.current = allStocks.filter(
      stock => filteredStocks.indexOf(stock) === -1
    )
    setFieldValue('stocks', filteredStocks)
  }, [
    currentSortingColumn,
    currentSortingMode,
    dateFilter,
    hourFilter,
    priceCategoryFilter,
  ])

  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const isSynchronized = Boolean(offer.lastProvider)

  const { page, setPage, previousPage, nextPage, currentPageItems, pageCount } =
    usePagination(values.stocks, STOCKS_PER_PAGE)

  return (
    <FieldArray
      name="stocks"
      render={arrayHelpers => (
        <>
          <table className={styles['stock-table']}>
            <caption className={styles['caption-table']}>
              Tableau d'édition des stocks
            </caption>

            <thead>
              <tr>
                <th className={styles['table-head']} scope="col">
                  <span className={styles['header-name']}>Date</span>

                  {areFiltersEnabled && (
                    <>
                      <SortArrow
                        onClick={() =>
                          onColumnHeaderClick(StocksEventFormSortingColumn.DATE)
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
                          onChange={date => {
                            setDateFilter(date)
                            onFilterChange()
                          }}
                          value={dateFilter}
                          filterVariant
                          aria-label="Filtrer par date"
                        />
                      </div>
                    </>
                  )}
                </th>

                <th className={styles['table-head']} scope="col">
                  <span className={styles['header-name']}>Horaire</span>

                  {areFiltersEnabled && (
                    <>
                      <SortArrow
                        onClick={() =>
                          onColumnHeaderClick(StocksEventFormSortingColumn.HOUR)
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
                          onChange={date => {
                            setHourFilter(date)
                            onFilterChange()
                          }}
                          value={hourFilter}
                          filterVariant
                          aria-label="Filtrer par horaire"
                        />
                      </div>
                    </>
                  )}
                </th>

                <th className={styles['table-head']} scope="col">
                  <span className={styles['header-name']}>Tarif</span>

                  {areFiltersEnabled && (
                    <>
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
                          name="priceCategoryFilter"
                          defaultOption={{ label: '', value: '' }}
                          options={priceCategoriesOptions}
                          value={priceCategoryFilter}
                          onChange={event => {
                            setPriceCategoryFilter(event.target.value)
                            onFilterChange()
                          }}
                          filterVariant
                          aria-label="Filtrer par tarif"
                        />
                      </div>
                    </>
                  )}
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

                  {areFiltersEnabled && (
                    <>
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
                      <div className={cn(styles['filter-input'])}>&nbsp;</div>
                    </>
                  )}
                </th>

                <th className={styles['table-head']} scope="col">
                  <span className={styles['header-name']}>
                    Quantité restante
                  </span>

                  {areFiltersEnabled && (
                    <>
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
                      <div className={cn(styles['filter-input'])}>&nbsp;</div>
                    </>
                  )}
                </th>

                <th
                  className={cn(
                    styles['table-head'],
                    styles['head-booking-quantity']
                  )}
                  scope="col"
                >
                  <span className={styles['header-name']}>Réservations</span>

                  {areFiltersEnabled && (
                    <>
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
                      <div className={cn(styles['filter-input'])}>&nbsp;</div>
                    </>
                  )}
                </th>

                <th></th>
              </tr>
            </thead>

            <tbody className={styles['table-body']}>
              {areFiltersActive && (
                <FilterResultsRow
                  colSpan={7}
                  onFiltersReset={() => {
                    setDateFilter(null)
                    setHourFilter(null)
                    setPriceCategoryFilter('')
                    onFilterChange()
                  }}
                  resultsCount={values.stocks.length}
                />
              )}

              {currentPageItems.map(
                (stockValues: StockEventFormValues, indexInPage) => {
                  const index = (page - 1) * STOCKS_PER_PAGE + indexInPage
                  const disableAllStockFields =
                    isSynchronized &&
                    mode === OFFER_WIZARD_MODE.EDITION &&
                    !stockValues.stockId

                  const stockFormValues = values.stocks[index]

                  if (disableAllStockFields) {
                    stockFormValues.readOnlyFields =
                      STOCK_EVENT_EDITION_EMPTY_SYNCHRONIZED_READ_ONLY_FIELDS
                  }
                  const { readOnlyFields } = stockFormValues

                  const onChangeBeginningDate = (
                    _name: string,
                    date: Date | null
                  ) => {
                    const stockBookingLimitDatetime =
                      stockFormValues.bookingLimitDatetime
                    /* istanbul ignore next: DEBT to fix */
                    if (stockBookingLimitDatetime === null) {
                      return
                    }
                    // tested but coverage don't see it.
                    /* istanbul ignore next */
                    if (date && isAfter(stockBookingLimitDatetime, date)) {
                      setTouched({
                        [`stocks[${index}]bookingLimitDatetime`]: true,
                      })
                      setFieldValue(
                        `stocks[${index}]bookingLimitDatetime`,
                        date
                      )
                    }
                  }

                  const beginningDate = stockFormValues.beginningDate
                  const actions = [
                    {
                      callback: async () => {
                        if (stockValues.stockId) {
                          /* istanbul ignore next: DEBT, TO FIX */
                          if (stockValues.bookingsQuantity > 0) {
                            setDeletingStockData({
                              deletingStock: stockValues,
                              deletingIndex: index,
                            })
                            deleteConfirmShow()
                          } else {
                            /* istanbul ignore next: DEBT, TO FIX */
                            onDeleteStock(stockValues, index)
                          }
                        } else {
                          arrayHelpers.remove(index)
                          /* istanbul ignore next: DEBT, TO FIX */
                          if (values.stocks.length === 1) {
                            arrayHelpers.push(STOCK_EVENT_FORM_DEFAULT_VALUES)
                          }
                        }
                      },
                      label: 'Supprimer le stock',
                      disabled:
                        !stockValues.isDeletable ||
                        isDisabled ||
                        disableAllStockFields,
                      Icon: TrashFilledIcon,
                    },
                  ]

                  return (
                    <tr className={styles['table-row']} key={index}>
                      <td className={styles['input-date']}>
                        <DatePicker
                          smallLabel
                          name={`stocks[${index}]beginningDate`}
                          label="Date"
                          isLabelHidden
                          classNameLabel={styles['field-layout-label']}
                          className={styles['field-layout-footer']}
                          minDateTime={today}
                          openingDateTime={today}
                          disabled={readOnlyFields.includes('beginningDate')}
                          onChange={onChangeBeginningDate}
                          hideFooter
                        />
                      </td>

                      <td className={styles['input-beginning-time']}>
                        <TimePicker
                          smallLabel
                          label="Horaire"
                          isLabelHidden
                          classNameLabel={styles['field-layout-label']}
                          className={styles['field-layout-footer']}
                          name={`stocks[${index}]beginningTime`}
                          disabled={readOnlyFields.includes('beginningTime')}
                          hideFooter
                        />
                      </td>

                      <td className={styles['input-price-category']}>
                        <Select
                          name={`stocks[${index}]priceCategoryId`}
                          options={priceCategoriesOptions}
                          smallLabel
                          label="Tarif"
                          isLabelHidden
                          classNameLabel={styles['field-layout-label']}
                          className={styles['field-layout-footer']}
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

                      <td className={styles['input-booking-limit-datetime']}>
                        <DatePicker
                          smallLabel
                          name={`stocks[${index}]bookingLimitDatetime`}
                          label="Date limite de réservation"
                          isLabelHidden
                          classNameLabel={styles['field-layout-label']}
                          className={styles['field-layout-footer']}
                          minDateTime={today}
                          maxDateTime={
                            beginningDate ? beginningDate : undefined
                          }
                          openingDateTime={today}
                          disabled={readOnlyFields.includes(
                            'bookingLimitDatetime'
                          )}
                          hideFooter
                        />
                      </td>

                      <td className={styles['input-quantity']}>
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
                          classNameLabel={styles['field-layout-label']}
                          className={styles['field-layout-footer']}
                          disabled={readOnlyFields.includes(
                            'remainingQuantity'
                          )}
                          type="number"
                          hasDecimal={false}
                          hideFooter
                        />
                      </td>

                      <td className={styles['field-info-bookings']}>
                        <TextInput
                          name={`stocks[${index}]bookingsQuantity`}
                          value={values.stocks[index].bookingsQuantity || 0}
                          readOnly
                          label="Réservations"
                          isLabelHidden
                          smallLabel
                          classNameLabel={styles['field-layout-label']}
                          className={styles['field-layout-footer']}
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

              {values.stocks.length === 0 && <NoResultsRow colSpan={7} />}
            </tbody>
          </table>

          <Pagination
            currentPage={page}
            pageCount={pageCount}
            onPreviousPageClick={previousPage}
            onNextPageClick={nextPage}
          />

          {deleteConfirmVisible && (
            <DialogStockEventDeleteConfirm
              /* istanbul ignore next: DEBT, TO FIX */
              onConfirm={async () => {
                /* istanbul ignore next: DEBT, TO FIX */
                if (deletingStockData !== null) {
                  const { deletingStock, deletingIndex } = deletingStockData
                  deletingStock.stockId &&
                    onDeleteStock(deletingStock, deletingIndex)
                }
                deleteConfirmHide()
              }}
              onCancel={deleteConfirmHide}
            />
          )}
        </>
      )}
    />
  )
}

export default StockFormList
