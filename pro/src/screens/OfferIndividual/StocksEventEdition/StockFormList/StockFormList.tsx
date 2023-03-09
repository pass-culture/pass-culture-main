import cn from 'classnames'
import { isAfter } from 'date-fns'
import { FieldArray, useFormikContext } from 'formik'
import React, { useCallback, useState } from 'react'

import { StockFormActions } from 'components/StockFormActions'
import { isOfferDisabled, OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { SelectOption } from 'custom_types/form'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import { useModal } from 'hooks/useModal'
import { EuroIcon, PlusCircleIcon } from 'icons'
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

export const STOCKS_PER_PAGE = 20

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
  const isPriceCategoriesActive = useActiveFeature(
    'WIP_ENABLE_MULTI_PRICE_STOCKS'
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
                    isPriceCategoriesActive &&
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

          <div className={styles['form-list']}>
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
                    setFieldValue(`stocks[${index}]bookingLimitDatetime`, date)
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
                  <div className={styles['stock-form-row']} key={index}>
                    <div className={styles['stock-form']}>
                      <DatePicker
                        smallLabel
                        name={`stocks[${index}]beginningDate`}
                        label="Date"
                        isLabelHidden={index !== 0}
                        className={cn(
                          styles['field-layout-align-self'],
                          styles['input-date']
                        )}
                        classNameLabel={styles['field-layout-label']}
                        classNameFooter={styles['field-layout-footer']}
                        minDateTime={today}
                        openingDateTime={today}
                        disabled={readOnlyFields.includes('beginningDate')}
                        onChange={onChangeBeginningDate}
                        hideHiddenFooter={true}
                      />

                      <TimePicker
                        smallLabel
                        label="Horaire"
                        isLabelHidden={index !== 0}
                        className={cn(
                          styles['input-beginning-time'],
                          styles['field-layout-align-self']
                        )}
                        classNameLabel={styles['field-layout-label']}
                        classNameFooter={styles['field-layout-footer']}
                        name={`stocks[${index}]beginningTime`}
                        disabled={readOnlyFields.includes('beginningTime')}
                        hideHiddenFooter={true}
                      />

                      {isPriceCategoriesActive ? (
                        <Select
                          name={`stocks[${index}]priceCategoryId`}
                          options={priceCategoriesOptions}
                          smallLabel
                          label="Tarif"
                          isLabelHidden={index !== 0}
                          className={cn(
                            styles['input-price-category'],
                            styles['field-layout-align-self']
                          )}
                          classNameLabel={styles['field-layout-label']}
                          classNameFooter={styles['field-layout-footer']}
                          defaultOption={{
                            label: 'Sélectionner un tarif',
                            value: '',
                          }}
                          disabled={
                            priceCategoriesOptions.length === 1 ||
                            readOnlyFields.includes('priceCategoryId')
                          }
                        />
                      ) : (
                        <TextInput
                          smallLabel
                          name={`stocks[${index}]price`}
                          label="Tarif"
                          isLabelHidden={index !== 0}
                          className={cn(
                            styles['input-price'],
                            styles['field-layout-align-self']
                          )}
                          classNameLabel={styles['field-layout-label']}
                          classNameFooter={styles['field-layout-footer']}
                          disabled={readOnlyFields.includes('price')}
                          rightIcon={() => <EuroIcon />}
                          type="number"
                          step="0.01"
                          hideHiddenFooter={true}
                          data-testid="input-price"
                        />
                      )}

                      <DatePicker
                        smallLabel
                        name={`stocks[${index}]bookingLimitDatetime`}
                        label="Date limite de réservation"
                        isLabelHidden={index !== 0}
                        className={cn(
                          styles['input-booking-limit-datetime'],
                          styles['field-layout-align-self']
                        )}
                        classNameLabel={styles['field-layout-label']}
                        classNameFooter={styles['field-layout-footer']}
                        minDateTime={today}
                        maxDateTime={beginningDate ? beginningDate : undefined}
                        openingDateTime={today}
                        disabled={readOnlyFields.includes(
                          'bookingLimitDatetime'
                        )}
                        hideHiddenFooter={true}
                      />

                      <TextInput
                        smallLabel
                        name={`stocks[${index}]remainingQuantity`}
                        label={
                          mode === OFFER_WIZARD_MODE.EDITION
                            ? 'Quantité restante'
                            : 'Quantité'
                        }
                        isLabelHidden={index !== 0}
                        placeholder="Illimité"
                        className={cn(
                          styles['input-quantity'],
                          styles['field-layout-align-self']
                        )}
                        classNameLabel={styles['field-layout-label']}
                        classNameFooter={styles['field-layout-footer']}
                        disabled={readOnlyFields.includes('remainingQuantity')}
                        type="number"
                        hasDecimal={false}
                        hideHiddenFooter={true}
                      />
                      {mode === OFFER_WIZARD_MODE.EDITION && (
                        <TextInput
                          name={`stocks[${index}]bookingsQuantity`}
                          value={values.stocks[index].bookingsQuantity || 0}
                          readOnly
                          label="Réservations"
                          isLabelHidden={index !== 0}
                          smallLabel
                          className={styles['field-info-bookings']}
                          classNameLabel={styles['field-layout-label']}
                          classNameFooter={styles['field-layout-footer']}
                          hideHiddenFooter
                        />
                      )}
                    </div>

                    {actions && actions.length > 0 && (
                      <div
                        className={cn(styles['stock-actions'], {
                          [styles['stock-first-action']]: index == 0,
                        })}
                      >
                        <StockFormActions
                          actions={actions}
                          disabled={false}
                          stockIndex={index}
                        />
                      </div>
                    )}
                  </div>
                )
              }
            )}
          </div>

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
