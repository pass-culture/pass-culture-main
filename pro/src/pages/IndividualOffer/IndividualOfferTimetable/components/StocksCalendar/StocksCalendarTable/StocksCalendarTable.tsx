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
import fullEditIcon from '@/icons/full-edit.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeTrashIcon from '@/icons/stroke-trash.svg'
import { getPriceCategoryName } from '@/pages/IndividualOffer/commons/getPriceCategoryOptions'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { type Column, Table, TableVariant } from '@/ui-kit/Table/Table'

import type { StocksTableFilters } from '../form/types'
import styles from './StocksCalendarTable.module.scss'
import { StocksCalendarTableEditStock } from './StocksCalendarTableEditStock/StocksCalendarTableEditStock'

export type StocksCalendarTableProps = {
  stocks: GetOfferStockResponseModel[]
  offer: GetIndividualOfferResponseModel
  isLoading: boolean
  hasNoStocks: boolean
  departmentCode: string
  mode: OFFER_WIZARD_MODE
  pagination: {
    currentPage: number
    pageCount: number
    onPageClick: (page: number) => void
  }
  checkedStocks: Set<number>
  updateCheckedStocks: (newStocks: Set<number>) => void
  onUpdateStock: (stock: EventStockUpdateBodyModel) => Promise<void>
  onDeleteStocks: (id: number[]) => void
  onUpdateFilters: (filters: StocksTableFilters) => void
}

export function StocksCalendarTable({
  stocks,
  offer,
  isLoading,
  hasNoStocks,
  departmentCode,
  mode,
  pagination,
  checkedStocks,
  updateCheckedStocks,
  onUpdateStock,
  onDeleteStocks,
  onUpdateFilters,
}: StocksCalendarTableProps) {
  const [isEditStockDialogOpen, setIsEditStockDialogOpen] = useState(false)
  const [stockOpenedInDialog, setStockOpenedInDialog] =
    useState<GetOfferStockResponseModel | null>(null)
  const [stockBeingDeleted, setStockBeingDeleted] =
    useState<GetOfferStockResponseModel | null>(null)

  const isCaledonian = useIsCaledonian()

  const openedStockTriggerRef = useRef<HTMLButtonElement | null>(null)

  const snackBar = useSnackBar()

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

  const columns: Column<GetOfferStockResponseModel>[] = [
    {
      id: 'beginningDate',
      label: 'Date',
      render: (stock) =>
        stock.beginningDatetime
          ? formatLocalTimeDateString(
              stock.beginningDatetime,
              departmentCode,
              FORMAT_DD_MM_YYYY
            )
          : 'Date invalide',
    },
    {
      id: 'time',
      label: 'Horaire',
      render: (stock) =>
        stock.beginningDatetime
          ? formatLocalTimeDateString(
              stock.beginningDatetime,
              departmentCode,
              FORMAT_HH_mm
            )
          : 'Horaire invalide',
    },
    {
      id: 'priceCategory',
      label: 'Tarif',
      render: (stock) => {
        const priceCategory = offer.priceCategories?.find(
          (p) => p.id === stock.priceCategoryId
        )

        return priceCategory
          ? getPriceCategoryName(priceCategory, isCaledonian)
          : 'Tarif invalide'
      },
    },
    {
      id: 'bookingLimit',
      label: 'Date limite de réservation',
      render: (stock) =>
        stock.bookingLimitDatetime
          ? formatLocalTimeDateString(
              stock.bookingLimitDatetime,
              departmentCode,
              FORMAT_DD_MM_YYYY
            )
          : 'Date invalide',
    },
    {
      id: 'quantityLeftOrTotal',
      label:
        mode === OFFER_WIZARD_MODE.CREATION ? 'Places' : 'Places restantes',
      render: (stock) => {
        if (stock.quantity === null) {
          return 'Illimité'
        }

        if (mode === OFFER_WIZARD_MODE.CREATION) {
          return stock.quantity
        }

        return (stock.quantity || 0) - stock.bookingsQuantity
      },
    },
  ]

  if (mode !== OFFER_WIZARD_MODE.CREATION) {
    columns.push({
      id: 'bookingsQuantity',
      label: 'Réservations',
      render: (stock) => stock.bookingsQuantity,
    })
  }

  if (mode !== OFFER_WIZARD_MODE.READ_ONLY) {
    columns.push({
      id: 'actions',
      label: 'Actions',
      render: (stock) => {
        const canDeleteStock = !isOfferDisabled(offer) && stock.isEventDeletable

        const canEditStock =
          mode === OFFER_WIZARD_MODE.EDITION &&
          !isOfferDisabled(offer) &&
          stock.beginningDatetime &&
          !isBefore(stock.beginningDatetime, new Date()) &&
          (!isOfferSynchronized(offer) || isOfferAllocineSynchronized(offer))

        if (!canEditStock && !canDeleteStock) {
          return null
        }

        return (
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
        )
      },
    })
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
      <Table
        columns={columns}
        selectable={mode === OFFER_WIZARD_MODE.CREATION}
        selectedIds={checkedStocks}
        onSelectionChange={(stocks) =>
          updateCheckedStocks(new Set(stocks.map((s) => s.id)))
        }
        data={stocks}
        isLoading={isLoading}
        variant={TableVariant.COLLAPSE}
        noResult={{
          message: 'Aucune date trouvée pour votre recherche',
          subtitle: 'Vous pouvez modifier votre recherche ou',
          resetMessage: 'Afficher toutes les dates',
          onFilterReset: () => onUpdateFilters({} as StocksTableFilters),
        }}
        noData={{
          hasNoData: hasNoStocks,
          message: {
            icon: '',
            title: 'Aucune date créée pour cet événement',
            subtitle: '',
          },
        }}
        pagination={pagination}
      />
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
