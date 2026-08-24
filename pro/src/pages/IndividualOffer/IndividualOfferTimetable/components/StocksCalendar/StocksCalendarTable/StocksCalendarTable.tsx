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
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from '@/commons/utils/date'
import { formatLocalTimeDateString } from '@/commons/utils/timezone'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import { SimpleModal } from '@/design-system/SimpleModal/SimpleModal'
import fullEditIcon from '@/icons/full-edit.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import strokeWarningIcon from '@/icons/stroke-warning.svg'
import { getPriceCategoryName } from '@/pages/IndividualOffer/commons/getPriceCategoryOptions'
import { type Column, Table, TableVariant } from '@/ui-kit/Table/Table'

import type { StocksTableFilters } from '../form/types'
import styles from './StocksCalendarTable.module.scss'
import {
  EDIT_STOCK_FORM_ID,
  StocksCalendarTableEditStock,
} from './StocksCalendarTableEditStock/StocksCalendarTableEditStock'

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
}: Readonly<StocksCalendarTableProps>) {
  type StockAction = 'delete' | 'editTime' | 'editDate' | 'editTimeDate'
  type WarningModalState = {
    stock: GetOfferStockResponseModel
    action: StockAction
    pendingStockUpdate?: EventStockUpdateBodyModel
  }

  const [isEditStockDialogOpen, setIsEditStockDialogOpen] = useState(false)
  const [stockOpenedInDialog, setStockOpenedInDialog] =
    useState<GetOfferStockResponseModel | null>(null)
  const [warningModalState, setWarningModalState] =
    useState<WarningModalState | null>(null)
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isVenueClosed = withVenueHelpers(selectedPartnerVenue).isClosed

  const isCaledonian = useIsCaledonian()

  const openedStockTriggerRef = useRef<HTMLButtonElement | null>(null)

  const snackBar = useSnackBar()

  const updateStock = async (stock: EventStockUpdateBodyModel) => {
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

  async function handleUpdateStock(stock: EventStockUpdateBodyModel) {
    if (
      stockOpenedInDialog?.beginningDatetime &&
      stockHasBookings(stockOpenedInDialog)
    ) {
      const action = getEditionAction(
        stockOpenedInDialog?.beginningDatetime,
        stock.beginningDatetime
      )
      if (action) {
        shouldOpenWarningModal(stockOpenedInDialog, action, stock)
        return
      }
    }

    await updateStock(stock)
  }

  const getEditionAction = (
    currentBeginningDatetime: string,
    updatedBeginningDatetime: string
  ): StockAction | null => {
    const hasDateChanged =
      formatLocalTimeDateString(
        currentBeginningDatetime,
        departmentCode,
        FORMAT_DD_MM_YYYY
      ) !==
      formatLocalTimeDateString(
        updatedBeginningDatetime,
        departmentCode,
        FORMAT_DD_MM_YYYY
      )

    const hasTimeChanged =
      formatLocalTimeDateString(
        currentBeginningDatetime,
        departmentCode,
        FORMAT_HH_mm
      ) !==
      formatLocalTimeDateString(
        updatedBeginningDatetime,
        departmentCode,
        FORMAT_HH_mm
      )

    if (hasDateChanged && hasTimeChanged) {
      return 'editTimeDate'
    }

    if (hasDateChanged) {
      return 'editDate'
    }

    if (hasTimeChanged) {
      return 'editTime'
    }

    return null
  }

  const getModalTitle = (action: StockAction) => {
    switch (action) {
      case 'delete':
        return `Supprimer la date et annuler les réservations existantes ?`
      case 'editTime':
        return `Modifier l'horaire des réservations existantes ?`
      case 'editDate':
        return 'Modifier la date des réservations existantes ?'
      case 'editTimeDate':
        return `Modifier la date et l’horaire des réservations existantes ?`
    }
  }

  const getModalContent = (action: StockAction) => {
    return {
      title: getModalTitle(action),
      description:
        action === 'delete'
          ? 'Cette action entrainera automatiquement l’annulation des réservations en cours et validées pour cette date. L’ensemble des bénéficiaires concernés sera averti par email.'
          : 'Cette action laissera la possibilité aux bénéficiaires concernés de se rétracter dans les prochaines 48 heures. Ils seront avertis par email.',
    }
  }

  const stockHasBookings = (stock: GetOfferStockResponseModel) =>
    stock.bookingsQuantity && stock.bookingsQuantity > 0

  const shouldOpenWarningModal = (
    stock: GetOfferStockResponseModel,
    action: StockAction,
    pendingStockUpdate?: EventStockUpdateBodyModel
  ) => {
    setIsEditStockDialogOpen(false)
    setWarningModalState({ stock, action, pendingStockUpdate })
  }

  const modalContent = warningModalState
    ? getModalContent(warningModalState.action)
    : null

  const getStockDateLabel = (stock: GetOfferStockResponseModel) =>
    stock.beginningDatetime
      ? formatLocalTimeDateString(
          stock.beginningDatetime,
          departmentCode,
          FORMAT_DD_MM_YYYY
        )
      : 'Date invalide'

  const getStockTimeLabel = (stock: GetOfferStockResponseModel) =>
    stock.beginningDatetime
      ? formatLocalTimeDateString(
          stock.beginningDatetime,
          departmentCode,
          FORMAT_HH_mm
        )
      : 'Horaire invalide'

  const columns: Column<GetOfferStockResponseModel>[] = [
    {
      id: 'beginningDate',
      label: 'Date',
      render: (stock) => getStockDateLabel(stock),
    },
    {
      id: 'time',
      label: 'Horaire',
      render: (stock) => getStockTimeLabel(stock),
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
        const canDeleteStock =
          !isOfferDisabled(offer) && stock.isEventDeletable && !isVenueClosed

        const canEditStock =
          mode === OFFER_WIZARD_MODE.EDITION &&
          !isOfferDisabled(offer) &&
          stock.beginningDatetime &&
          !isBefore(stock.beginningDatetime, new Date()) &&
          (!isOfferSynchronized(offer) || isOfferAllocineSynchronized(offer)) &&
          !isVenueClosed

        if (!canEditStock && !canDeleteStock) {
          return null
        }

        return (
          <div className={styles['table-actions']}>
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
                onClick={() => {
                  if (stockHasBookings(stock)) {
                    shouldOpenWarningModal(stock, 'delete')
                  } else {
                    onDeleteStocks([stock.id])
                  }
                }}
              />
            )}
          </div>
        )
      },
    })
  }

  return (
    <>
      {/* The modal must be outside of the table rows, otherwise it creates a modal root for each line */}
      <DetailedModal
        title="Modifier la date"
        isOpen={isEditStockDialogOpen}
        onClose={() => {
          if (warningModalState) {
            return
          }

          setTimeout(() => {
            //  Re-focus the trigger of the dialog when it's closed
            openedStockTriggerRef.current?.focus()
          })
          setIsEditStockDialogOpen(false)
        }}
        primaryAction={
          <Button type="submit" form={EDIT_STOCK_FORM_ID} label="Valider" />
        }
        secondaryAction={
          <Button
            type="button"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            onClick={() => {
              setTimeout(() => {
                openedStockTriggerRef.current?.focus()
              })
              setIsEditStockDialogOpen(false)
            }}
            label="Annuler"
          />
        }
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
      </DetailedModal>
      <Table
        columns={columns}
        title="Horaires, tarifs et stocks"
        selectable={mode === OFFER_WIZARD_MODE.CREATION}
        selectedIds={checkedStocks}
        onSelectionChange={(stocks) =>
          updateCheckedStocks(new Set(stocks.map((s) => s.id)))
        }
        getRowSelectionDateTime={(stock) =>
          `${getStockDateLabel(stock)} à ${getStockTimeLabel(stock)}`
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
      <SimpleModal
        iconPath={strokeWarningIcon}
        title={modalContent?.title ?? ''}
        isOpen={Boolean(warningModalState)}
        onClose={() => {
          setWarningModalState(null)
        }}
        actionButtons={[
          <Button
            onClick={() => {
              setWarningModalState(null)
            }}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label={'Annuler'}
            key="cancel"
          />,
          <Button
            onClick={async () => {
              if (!warningModalState) {
                return
              }

              if (warningModalState.action === 'delete') {
                onDeleteStocks([warningModalState.stock.id])
              } else if (warningModalState.pendingStockUpdate) {
                await updateStock(warningModalState.pendingStockUpdate)
              }

              setWarningModalState(null)
            }}
            variant={ButtonVariant.PRIMARY}
            color={ButtonColor.DANGER}
            label={
              warningModalState?.action === 'delete'
                ? 'Confirmer la suppression'
                : 'Confirmer la modification'
            }
            key="confirm"
          />,
        ]}
      >
        {modalContent?.description ?? ''}
      </SimpleModal>
    </>
  )
}
