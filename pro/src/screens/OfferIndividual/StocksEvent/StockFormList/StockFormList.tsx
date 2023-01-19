import { FieldArray, useFormikContext } from 'formik'
import React, { useCallback, useState } from 'react'

import {
  StockEventForm,
  IStockEventFormValues,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
} from 'components/StockEventForm'
import { StockEventFormRow } from 'components/StockEventFormRow'
import { isOfferDisabled, OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferIndividual } from 'core/Offers/types'
import { useOfferWizardMode } from 'hooks'
import { useModal } from 'hooks/useModal'
import { IconPlusCircle } from 'icons'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { DialogStockDeleteConfirm } from 'screens/OfferIndividual/DialogStockDeleteConfirm'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Pagination } from 'ui-kit/Pagination'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import styles from './StockFormList.module.scss'

interface IStockFormListProps {
  offer: IOfferIndividual
  onDeleteStock: (
    stockValues: IStockEventFormValues,
    stockIndex: number
  ) => Promise<void>
}

export const STOCKS_PER_PAGE = 20

const StockFormList = ({ offer, onDeleteStock }: IStockFormListProps) => {
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
  const { values } = useFormikContext<{
    stocks: IStockEventFormValues[]
  }>()
  const today = getLocalDepartementDateTimeFromUtc(
    getToday(),
    offer.venue.departmentCode
  )
  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const isSynchronized = Boolean(offer.lastProvider)

  const [page, setPage] = useState(1)
  const previousPage = useCallback(() => setPage(page - 1), [page])
  const nextPage = useCallback(() => setPage(page + 1), [page])
  const stocksPage = values.stocks.slice(
    (page - 1) * STOCKS_PER_PAGE,
    page * STOCKS_PER_PAGE
  )

  return (
    <FieldArray
      name="stocks"
      render={arrayHelpers => (
        <>
          <Button
            variant={ButtonVariant.TERNARY}
            Icon={IconPlusCircle}
            onClick={() =>
              arrayHelpers.unshift(STOCK_EVENT_FORM_DEFAULT_VALUES)
            }
            disabled={isSynchronized}
          >
            Ajouter une date
          </Button>

          <div className={styles['form-list']}>
            {stocksPage.map((stockValues: IStockEventFormValues, index) => {
              const disableAllStockFields =
                isSynchronized &&
                mode === OFFER_WIZARD_MODE.EDITION &&
                !stockValues.stockId

              return (
                <StockEventFormRow
                  key={`${stockValues.stockId}-${index}`}
                  stockIndex={index}
                  actions={[
                    {
                      callback: async () => {
                        if (stockValues.stockId) {
                          /* istanbul ignore next: DEBT, TO FIX */
                          if (parseInt(stockValues.bookingsQuantity) > 0) {
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
                  ]}
                  actionDisabled={false}
                  showStockInfo={mode === OFFER_WIZARD_MODE.EDITION}
                >
                  <StockEventForm
                    today={today}
                    stockIndex={index}
                    disableAllStockFields={disableAllStockFields}
                  />
                </StockEventFormRow>
              )
            })}
          </div>

          <Pagination
            currentPage={page}
            pageCount={Math.ceil(values.stocks.length / STOCKS_PER_PAGE)}
            onPreviousPageClick={previousPage}
            onNextPageClick={nextPage}
          />

          {deleteConfirmVisible && (
            <DialogStockDeleteConfirm
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
              isEvent={true}
            />
          )}
        </>
      )}
    />
  )
}

export default StockFormList
