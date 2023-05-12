import cn from 'classnames'
import { isAfter } from 'date-fns'
import { FieldArray, useFormikContext } from 'formik'
import React, { useCallback, useState } from 'react'

import { StockFormActions } from 'components/StockFormActions'
import { isOfferDisabled, OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { SelectOption } from 'custom_types/form'
import { useOfferWizardMode } from 'hooks'
import { useModal } from 'hooks/useModal'
import { PlusCircleIcon } from 'icons'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import DialogStockEventDeleteConfirm from 'screens/OfferIndividual/DialogStockDeleteConfirm/DialogStockEventDeleteConfirm'
import { Button, DatePicker, Select, TextInput, TimePicker } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Pagination } from 'ui-kit/Pagination'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import { STOCK_EVENT_EDITION_EMPTY_SYNCHRONIZED_READ_ONLY_FIELDS } from './constants'
import styles from './StockFormList.module.scss'

import { IStockEventFormValues, STOCK_EVENT_FORM_DEFAULT_VALUES } from './'

interface IStockFormListProps {
  offer: IOfferIndividual
  onDeleteStock: (
    stockValues: IStockEventFormValues,
    index: number
  ) => Promise<void>
  priceCategoriesOptions: SelectOption[]
}

const STOCKS_PER_PAGE = 20

const StockFormList = ({
  offer,
  onDeleteStock,
  priceCategoriesOptions,
}: IStockFormListProps) => {
  const {
    visible: deleteConfirmVisible,
    showModal: deleteConfirmShow,
    hideModal: deleteConfirmHide,
  } = useModal()
  const mode = useOfferWizardMode()
  const [deletingStockData, setDeletingStockData] = useState<{
    deletingStock: IStockEventFormValues
    deletingIndex: number
  } | null>(null)
  const { values, setFieldValue, setTouched } = useFormikContext<{
    stocks: IStockEventFormValues[]
  }>()
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departmentCode
  )
  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const isSynchronized = Boolean(offer.lastProvider)

  const [page, setPage] = useState(1)
  const previousPage = useCallback(() => setPage(page => page - 1), [])
  const nextPage = useCallback(() => setPage(page => page + 1), [])
  const stocksPage = values.stocks.slice(
    (page - 1) * STOCKS_PER_PAGE,
    page * STOCKS_PER_PAGE
  )

  return (
    <FieldArray
      name="stocks"
      render={arrayHelpers => (
        <>
          <div className={styles['button-row']}>
            <Button
              variant={ButtonVariant.TERNARY}
              Icon={PlusCircleIcon}
              onClick={() =>
                arrayHelpers.unshift({
                  ...STOCK_EVENT_FORM_DEFAULT_VALUES,
                  priceCategoryId:
                    priceCategoriesOptions.length === 1
                      ? priceCategoriesOptions[0].value
                      : '',
                })
              }
              disabled={isSynchronized || isDisabled}
            >
              Ajouter une date
            </Button>
            <div>{values.stocks.length} dates</div>
          </div>

          <table className={styles['stock-table']}>
            <caption className={styles['caption-table']}>
              Tableau d'édition des stocks
            </caption>
            <thead>
              <tr>
                <th className={styles['table-head']} scope="col">
                  Date
                </th>
                <th className={styles['table-head']} scope="col">
                  Horaire
                </th>
                <th className={styles['table-head']} scope="col">
                  Tarif
                </th>
                <th
                  className={cn(
                    styles['table-head'],
                    styles['head-booking-limit-datetime']
                  )}
                  scope="col"
                >
                  Date limite de réservation
                </th>
                <th className={styles['table-head']} scope="col">
                  Quantité restante
                </th>
                <th className={styles['table-head']} scope="col">
                  Réservations
                </th>
                <th></th>
              </tr>
            </thead>
            <tbody className={styles['table-body']}>
              {stocksPage.map(
                (stockValues: IStockEventFormValues, indexInPage) => {
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
                      {mode === OFFER_WIZARD_MODE.EDITION && (
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
                      )}

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
            </tbody>
          </table>

          <Pagination
            currentPage={page}
            pageCount={Math.ceil(values.stocks.length / STOCKS_PER_PAGE)}
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
