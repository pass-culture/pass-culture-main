import { FieldArray, useFormikContext } from 'formik'
import React, { useState } from 'react'

import {
  StockEventForm,
  setFormReadOnlyFields,
  IStockEventFormValues,
  STOCK_EVENT_FORM_DEFAULT_VALUES,
} from 'components/StockEventForm'
import { StockFormRow } from 'components/StockFormRow'
import { IOfferIndividual } from 'core/Offers/types'
import { useModal } from 'hooks/useModal'
import { IconPlusCircle } from 'icons'
import { DialogStockDeleteConfirm } from 'screens/OfferIndividual/DialogStockDeleteConfirm'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { getToday } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

import styles from './StockFormList.module.scss'

interface IStockFormListProps {
  offer: IOfferIndividual
  onDeleteStock: (stockValues: IStockEventFormValues) => Promise<void>
}

const StockFormList = ({ offer, onDeleteStock }: IStockFormListProps) => {
  const {
    visible: deleteConfirmVisible,
    showModal: deleteConfirmShow,
    hideModal: deleteConfirmHide,
  } = useModal()
  const [deletingStockData, setDeletingStockDate] = useState<{
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

  return (
    <FieldArray
      name="stocks"
      render={arrayHelpers => (
        <>
          <Button
            variant={ButtonVariant.TERNARY}
            Icon={IconPlusCircle}
            onClick={() => arrayHelpers.push(STOCK_EVENT_FORM_DEFAULT_VALUES)}
          >
            Ajouter une date
          </Button>

          <div className={styles['form-list']}>
            {values.stocks.map((stockValues: IStockEventFormValues, index) => (
              <StockFormRow
                key={index}
                Form={
                  <StockEventForm
                    today={today}
                    readOnlyFields={setFormReadOnlyFields(
                      offer,
                      stockValues.beginningDate || null,
                      today
                    )}
                    fieldPrefix={`stocks[${index}].`}
                  />
                }
                actions={
                  values.stocks.length > 1 && stockValues.isDeletable
                    ? [
                        {
                          callback: async () => {
                            setDeletingStockDate({
                              deletingStock: stockValues,
                              deletingIndex: index,
                            })
                            stockValues.stockId
                              ? deleteConfirmShow()
                              : arrayHelpers.remove(index)
                          },
                          label: 'Supprimer',
                        },
                      ]
                    : []
                }
                actionDisabled={false}
              />
            ))}
          </div>

          {deleteConfirmVisible && (
            <DialogStockDeleteConfirm
              onConfirm={() => {
                if (deletingStockData !== null) {
                  const { deletingStock, deletingIndex } = deletingStockData
                  deletingStock.stockId && onDeleteStock(deletingStock)
                  arrayHelpers.remove(deletingIndex)
                }
                deleteConfirmHide()
              }}
              onCancel={deleteConfirmHide}
              isEvent={true}
            />
          )}
        </>
      )}
    ></FieldArray>
  )
}

export default StockFormList
