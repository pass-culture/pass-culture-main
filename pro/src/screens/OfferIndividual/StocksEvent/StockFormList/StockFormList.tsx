import { FieldArray, useFormikContext } from 'formik'
import React, { useState } from 'react'

import {
  StockEventForm,
  setFormReadOnlyFields,
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
  const mode = useOfferWizardMode()
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
  const isDisabled = offer.status ? isOfferDisabled(offer.status) : false
  const isSynchronized = Boolean(offer.lastProvider)

  return (
    <FieldArray
      name="stocks"
      render={arrayHelpers => (
        <>
          <Button
            variant={ButtonVariant.TERNARY}
            Icon={IconPlusCircle}
            onClick={() => arrayHelpers.push(STOCK_EVENT_FORM_DEFAULT_VALUES)}
            disabled={isSynchronized}
          >
            Ajouter une date
          </Button>

          <div className={styles['form-list']}>
            {values.stocks.map((stockValues: IStockEventFormValues, index) => (
              <StockEventFormRow
                key={index}
                stockIndex={index}
                Form={
                  <StockEventForm
                    today={today}
                    readOnlyFields={setFormReadOnlyFields(
                      offer,
                      stockValues.beginningDate || null,
                      today
                    )}
                    stockIndex={index}
                  />
                }
                actions={[
                  {
                    callback: async () => {
                      setDeletingStockDate({
                        deletingStock: stockValues,
                        deletingIndex: index,
                      })
                      if (stockValues.stockId) {
                        deleteConfirmShow()
                      } else {
                        arrayHelpers.remove(index)
                        if (values.stocks.length === 1) {
                          arrayHelpers.push(STOCK_EVENT_FORM_DEFAULT_VALUES)
                        }
                      }
                    },
                    label: 'Supprimer le stock',
                    disabled:
                      !stockValues.isDeletable || isDisabled || isSynchronized,
                    Icon: TrashFilledIcon,
                  },
                ]}
                actionDisabled={false}
                showStockInfo={mode === OFFER_WIZARD_MODE.EDITION}
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
                if (values.stocks.length === 1) {
                  arrayHelpers.push(STOCK_EVENT_FORM_DEFAULT_VALUES)
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
