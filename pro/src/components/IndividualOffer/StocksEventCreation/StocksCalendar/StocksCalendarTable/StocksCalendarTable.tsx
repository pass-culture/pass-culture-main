import { isBefore } from 'date-fns'
import { useRef, useState } from 'react'

import {
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
  EventStockCreateBodyModel,
} from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { useNotification } from 'commons/hooks/useNotification'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm, removeTime } from 'commons/utils/date'
import { formatLocalTimeDateString } from 'commons/utils/timezone'
import { getPriceCategoryName } from 'components/IndividualOffer/StocksEventEdition/getPriceCategoryOptions'
import fullEditIcon from 'icons/full-edit.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { Checkbox } from 'ui-kit/formV2/Checkbox/Checkbox'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './StocksCalendarTable.module.scss'
import { StocksCalendarTableEditStock } from './StocksCalendarTableEditStock/StocksCalendarTableEditStock'

export type StocksCalendarTableProps = {
  stocks: GetOfferStockResponseModel[]
  offer: GetIndividualOfferResponseModel
  onDeleteStocks: (id: number[]) => void
  checkedStocks: Set<number>
  updateCheckedStocks: (newStocks: Set<number>) => void
  departmentCode: string
  mode: OFFER_WIZARD_MODE
  onUpdateStock: (stock: EventStockCreateBodyModel) => Promise<void>
}

export function StocksCalendarTable({
  stocks,
  offer,
  onDeleteStocks,
  onUpdateStock,
  checkedStocks,
  updateCheckedStocks,
  departmentCode,
  mode,
}: StocksCalendarTableProps) {
  const [isEditStockDialogOpen, setIsEditStockDialogOpen] = useState(false)
  const [stockOpenedInDialog, setStockOpenedInDialog] =
    useState<GetOfferStockResponseModel | null>(null)

  const openedStockTriggerRef = useRef<HTMLButtonElement | null>(null)

  const notify = useNotification()

  function handleStockCheckboxClicked(stockId: number) {
    const newChecked = new Set(Array.from(checkedStocks))
    if (checkedStocks.has(stockId)) {
      newChecked.delete(stockId)
    } else {
      newChecked.add(stockId)
    }
    updateCheckedStocks(newChecked)
  }

  async function handleUpdateStock(stock: EventStockCreateBodyModel) {
    try {
      await onUpdateStock(stock)
    } catch {
      notify.error(
        'Une erreur est survenue pendant la modification de la date.'
      )
    } finally {
      setIsEditStockDialogOpen(false)
    }
  }

  if (stocks.length === 0) {
    return (
      <div className={styles['no-data']}>
        <SvgIcon
          src={strokeSearchIcon}
          alt=""
          className={styles['no-data-icon']}
        />
        <p className={styles['bold']}>Aucune date trouvée</p>
        <p>
          Vous pouvez modifier vos filtres pour lancer une nouvelle recherche
        </p>
      </div>
    )
  }

  return (
    <div className={styles['container']}>
      {/* The dialog must be outside of the table rows, otherwise radix created a dialog root for each line */}
      <DialogBuilder
        title="Modifier la date"
        variant="drawer"
        open={isEditStockDialogOpen}
        onOpenChange={(isOpen) => {
          if (!isOpen) {
            setTimeout(() => {
              //  Re-focus the trigger of the dialog when it's closed
              openedStockTriggerRef.current?.focus()
            })
          }
          setIsEditStockDialogOpen(isOpen)
        }}
      >
        {stockOpenedInDialog && (
          <StocksCalendarTableEditStock
            stock={stockOpenedInDialog}
            departmentCode={departmentCode}
            priceCategories={offer.priceCategories}
            onUpdateStock={handleUpdateStock}
          />
        )}
      </DialogBuilder>
      <table className={styles['table']}>
        <thead className={styles['thead']}>
          <tr>
            <th className={styles['thead-th']}>
              <div className={styles['thead-th-date']}>
                {mode === OFFER_WIZARD_MODE.CREATION && (
                  <Checkbox
                    label={
                      <span className={styles['visually-hidden']}>
                        Sélectionner tous les stocks
                      </span>
                    }
                    partialCheck={
                      checkedStocks.size < stocks.length &&
                      checkedStocks.size > 0
                    }
                    checked={checkedStocks.size === stocks.length}
                    onChange={() => {
                      if (checkedStocks.size < stocks.length) {
                        updateCheckedStocks(new Set(stocks.map((s) => s.id)))
                      } else {
                        updateCheckedStocks(new Set())
                      }
                    }}
                    name="select-all"
                  />
                )}
                Date
              </div>
            </th>
            <th className={styles['thead-th']}>Horaire</th>
            <th className={styles['thead-th']}>Tarif</th>
            <th className={styles['thead-th']}>Date limite de réservation</th>
            <th className={styles['thead-th']}>
              {mode === OFFER_WIZARD_MODE.CREATION
                ? 'Place'
                : 'Quantité restante'}
            </th>
            {mode !== OFFER_WIZARD_MODE.CREATION && (
              <th className={styles['thead-th']}>Réservations</th>
            )}
            {mode !== OFFER_WIZARD_MODE.READ_ONLY && (
              <th className={styles['thead-th']}>Actions</th>
            )}
          </tr>
        </thead>
        <tbody className={styles['tbody']}>
          {stocks.map((stock) => {
            const priceCaregory = offer.priceCategories?.find(
              (p) => p.id === stock.priceCategoryId
            )

            const checkboxDateLabel = stock.beginningDatetime ? (
              <span className={styles['tbody-td-date']}>
                {formatLocalTimeDateString(
                  stock.beginningDatetime,
                  departmentCode,
                  FORMAT_DD_MM_YYYY
                )}
              </span>
            ) : (
              'Date invalide'
            )

            const canDeleteStock =
              mode !== OFFER_WIZARD_MODE.READ_ONLY &&
              !isOfferDisabled(offer.status) &&
              stock.isEventDeletable

            const canEditStock =
              mode === OFFER_WIZARD_MODE.EDITION &&
              !isOfferDisabled(offer.status) &&
              stock.beginningDatetime &&
              !isBefore(stock.beginningDatetime, removeTime(new Date()))

            return (
              <tr key={stock.id} className={styles['tr']}>
                <td className={styles['tbody-td']}>
                  {mode === OFFER_WIZARD_MODE.CREATION ? (
                    <Checkbox
                      label={checkboxDateLabel}
                      checked={checkedStocks.has(stock.id)}
                      onChange={() => handleStockCheckboxClicked(stock.id)}
                      name="select-stock"
                    />
                  ) : (
                    checkboxDateLabel
                  )}
                </td>
                <td className={styles['tbody-td']}>
                  {stock.beginningDatetime
                    ? formatLocalTimeDateString(
                        stock.beginningDatetime,
                        departmentCode,
                        FORMAT_HH_mm
                      )
                    : 'Horaire invalide'}
                </td>
                <td className={styles['tbody-td']}>
                  {priceCaregory
                    ? getPriceCategoryName(priceCaregory)
                    : 'Tarif invalide'}
                </td>
                <td className={styles['tbody-td']}>
                  {stock.bookingLimitDatetime
                    ? formatLocalTimeDateString(
                        stock.bookingLimitDatetime,
                        departmentCode,
                        FORMAT_DD_MM_YYYY
                      )
                    : 'Date invalide'}
                </td>
                <td className={styles['tbody-td']}>
                  {stock.quantity === null
                    ? 'Illimité'
                    : mode === OFFER_WIZARD_MODE.CREATION
                      ? stock.quantity
                      : (stock.quantity || 0) - stock.bookingsQuantity}
                </td>
                {mode !== OFFER_WIZARD_MODE.CREATION && (
                  <td className={styles['tbody-td']}>
                    {stock.bookingsQuantity}
                  </td>
                )}

                {mode !== OFFER_WIZARD_MODE.READ_ONLY && (
                  <td className={styles['tbody-td']}>
                    <div className={styles['tbody-td-actions']}>
                      {canEditStock && (
                        <ListIconButton
                          icon={fullEditIcon}
                          tooltipContent="Modifier la date"
                          ref={
                            stock.id === stockOpenedInDialog?.id
                              ? openedStockTriggerRef
                              : undefined
                          }
                          onClick={() => {
                            setStockOpenedInDialog(stock)
                            setIsEditStockDialogOpen(true)
                          }}
                        />
                      )}
                      {canDeleteStock && (
                        <ListIconButton
                          icon={fullTrashIcon}
                          tooltipContent="Supprimer la date"
                          onClick={() => onDeleteStocks([stock.id])}
                        />
                      )}
                    </div>
                  </td>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
