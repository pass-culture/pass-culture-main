import { isBefore } from 'date-fns'
import { useRef, useState } from 'react'

import type {
  EventStockUpdateBodyModel,
  GetIndividualOfferResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { isOfferDisabled } from '@/commons/core/Offers/utils/isOfferDisabled'
import {
  isOfferAllocineSynchronized,
  isOfferSynchronized,
} from '@/commons/core/Offers/utils/typology'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from '@/commons/utils/date'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import fullEditIcon from '@/icons/full-edit.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeSearchIcon from '@/icons/stroke-search.svg'
import strokeTrashIcon from '@/icons/stroke-trash.svg'
import { getPriceCategoryName } from '@/pages/IndividualOffer/commons/getPriceCategoryOptions'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

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
  onUpdateStock: (stock: EventStockUpdateBodyModel) => Promise<void>
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
  const [stockBeingDeleted, setStockBeingDeleted] =
    useState<GetOfferStockResponseModel | null>(null)

  const isCaledonian = useIsCaledonian()

  const openedStockTriggerRef = useRef<HTMLButtonElement | null>(null)

  const snackBar = useSnackBar()

  function handleStockCheckboxClicked(stockId: number) {
    const newChecked = new Set(Array.from(checkedStocks))
    if (checkedStocks.has(stockId)) {
      newChecked.delete(stockId)
    } else {
      newChecked.add(stockId)
    }
    updateCheckedStocks(newChecked)
  }

  async function handleUpdateStock(stock: EventStockUpdateBodyModel) {
    try {
      await onUpdateStock(stock)
    } catch {
      snackBar.error(
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
            offer={offer}
          />
        )}
      </DialogBuilder>
      {mode === OFFER_WIZARD_MODE.CREATION && (
        <div className={styles['select-all']}>
          <Checkbox
            label="Tout sélectionner"
            indeterminate={
              checkedStocks.size < stocks.length && checkedStocks.size > 0
            }
            checked={checkedStocks.size === stocks.length}
            onChange={() => {
              if (checkedStocks.size < stocks.length) {
                updateCheckedStocks(new Set(stocks.map((s) => s.id)))
              } else {
                updateCheckedStocks(new Set())
              }
            }}
          />
        </div>
      )}
      <table className={styles['table']}>
        <thead className={styles['thead']}>
          <tr>
            <th className={styles['thead-th']}>
              <div className={styles['thead-th-date']}>Date</div>
            </th>
            <th className={styles['thead-th']}>Horaire</th>
            <th className={styles['thead-th']}>Tarif</th>
            <th className={styles['thead-th']}>Date limite de réservation</th>
            <th className={styles['thead-th']}>
              {mode === OFFER_WIZARD_MODE.CREATION
                ? 'Places'
                : 'Places restantes'}
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
            const priceCategory = offer.priceCategories?.find(
              (p) => p.id === stock.priceCategoryId
            )

            const checkboxDateLabel = stock.beginningDatetime
              ? formatLocalTimeDateString(
                  stock.beginningDatetime,
                  departmentCode,
                  FORMAT_DD_MM_YYYY
                )
              : 'Date invalide'

            const canDeleteStock =
              mode !== OFFER_WIZARD_MODE.READ_ONLY &&
              !isOfferDisabled(offer) &&
              stock.isEventDeletable

            const canEditStock =
              mode === OFFER_WIZARD_MODE.EDITION &&
              !isOfferDisabled(offer) &&
              stock.beginningDatetime &&
              !isBefore(stock.beginningDatetime, new Date()) &&
              (!isOfferSynchronized(offer) ||
                isOfferAllocineSynchronized(offer))

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
                  {priceCategory
                    ? getPriceCategoryName(priceCategory, isCaledonian)
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
                        <Button
                          variant={ButtonVariant.SECONDARY}
                          color={ButtonColor.NEUTRAL}
                          size={ButtonSize.SMALL}
                          icon={fullEditIcon}
                          tooltip="Modifier la date"
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
                        <Button
                          variant={ButtonVariant.SECONDARY}
                          color={ButtonColor.NEUTRAL}
                          size={ButtonSize.SMALL}
                          icon={fullTrashIcon}
                          tooltip="Supprimer la date"
                          onClick={() => setStockBeingDeleted(stock)}
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
      <ConfirmDialog
        onCancel={() => {
          setStockBeingDeleted(null)
        }}
        onConfirm={() => {
          if (stockBeingDeleted) {
            onDeleteStocks([stockBeingDeleted.id])
          }
          setStockBeingDeleted(null)
        }}
        title="Êtes-vous sûr de vouloir supprimer cette date ?"
        confirmText="Confirmer la suppression"
        cancelText="Annuler"
        icon={strokeTrashIcon}
        open={Boolean(stockBeingDeleted)}
      >
        {stockBeingDeleted?.bookingsQuantity &&
        stockBeingDeleted.bookingsQuantity > 0 ? (
          <>
            <p className={styles['delete-warning-block']}>
              {'Elle ne sera plus disponible à la réservation et '}
              <strong>
                entraînera l’annulation des réservations en cours et validées !
              </strong>
            </p>
            <p>
              L’ensemble des utilisateurs concernés sera automatiquement averti
              par email.
            </p>
          </>
        ) : null}
      </ConfirmDialog>
    </div>
  )
}
