import { type Dispatch, type SetStateAction, useState } from 'react'
import useSWR, { mutate } from 'swr'

import { api } from '@/apiClient/api'
import {
  type EventStockUpdateBodyModel,
  type GetIndividualOfferWithAddressResponseModel,
  StocksOrderedBy,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  GET_OFFER_QUERY_KEY,
  GET_STOCKS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { useNotification } from '@/commons/hooks/useNotification'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { pluralize } from '@/commons/utils/pluralize'
import { convertTimeFromVenueTimezoneToUtc } from '@/commons/utils/timezone'
import strokeAddCalendarIcon from '@/icons/stroke-add-calendar.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'
import { Pagination } from '@/ui-kit/Pagination/Pagination'
import { Spinner } from '@/ui-kit/Spinner/Spinner'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { onSubmit } from './form/onSubmit'
import type {
  RecurrenceFormValues,
  StocksTableFilters,
  StocksTableSort,
} from './form/types'
import { RecurrenceForm } from './RecurrenceForm/RecurrenceForm'
import styles from './StocksCalendar.module.scss'
import { StocksCalendarActionsBar } from './StocksCalendarActionsBar/StocksCalendarActionsBar'
import { StocksCalendarFilters } from './StocksCalendarFilters/StocksCalendarFilters'
import { StocksCalendarTable } from './StocksCalendarTable/StocksCalendarTable'

const STOCKS_PER_PAGE = 20

export type StocksCalendarProps = {
  offer: GetIndividualOfferWithAddressResponseModel
  mode: OFFER_WIZARD_MODE
  timetableTypeRadioGroupShown: boolean
}

export function StocksCalendar({
  offer,
  mode,
  timetableTypeRadioGroupShown,
}: StocksCalendarProps) {
  const [page, setPage] = useState(1)
  const [checkedStocks, setCheckedStocks] = useState(new Set<number>())
  const [appliedFilters, setAppliedFilters] = useState<StocksTableFilters>({})
  const [appliedSort, setAppliedSort] = useState<StocksTableSort>({
    sort: StocksOrderedBy.DATE,
  })
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const departmentCode = getDepartmentCode(offer)

  const queryKeys: [
    string,
    number,
    number,
    StocksTableFilters,
    StocksTableSort,
  ] = [GET_STOCKS_QUERY_KEY, offer.id, page, appliedFilters, appliedSort]

  const { data, isLoading } = useSWR(
    queryKeys,
    ([, offerId, pageNum, filters, sortType]) =>
      api.getStocks(
        offerId,
        filters.date || undefined,
        filters.time
          ? convertTimeFromVenueTimezoneToUtc(filters.time, departmentCode)
          : undefined,
        filters.priceCategoryId ? Number(filters.priceCategoryId) : undefined,
        sortType.sort,
        sortType.orderByDesc,
        pageNum || 1,
        STOCKS_PER_PAGE
      ),
    {
      //  Display previous data in the table until the new data has loaded so that
      //  the scroll position in the table remains the same in-between pagination loads
      keepPreviousData: true,
      onSuccess: () => {
        setCheckedStocks(new Set())
      },
    }
  )

  async function deleteStocks(ids: number[]) {
    await api.deleteStocks(offer.id, { ids_to_delete: ids })

    if (
      page > 1 &&
      data?.stockCount &&
      data.stockCount - ids.length <= (page - 1) * STOCKS_PER_PAGE
    ) {
      //  Descrease the page number if deleting the ids would leave the user on an empty stocks page
      setPage((p) => p - 1)
    }

    notify.success(
      ids.length === 1
        ? 'Une date a été supprimée'
        : `${ids.length} dates ont été supprimées`
    )
    await mutate(queryKeys)
    await mutate([GET_OFFER_QUERY_KEY, offer.id])
  }

  async function updateStock(stock: EventStockUpdateBodyModel) {
    try {
      const updatedStocks = await api.bulkUpdateEventStocks({
        offerId: offer.id,
        stocks: [stock],
      })

      if (updatedStocks.stocks_count === 0) {
        notify.error('Aucune date n’a pu être modifiée')
        return
      }

      notify.success('Les modifications ont été enregistrées')

      await mutate(queryKeys)
    } catch {
      notify.error('Une erreur est survenue lors de la modification des dates')
    }
  }

  const handleSubmitRecurrenceFormDrawer = async (
    values: RecurrenceFormValues
  ) => {
    const departmentCode = getDepartmentCode(offer)

    logEvent(Events.CLICKED_VALIDATE_ADD_RECURRENCE_DATES, {
      recurrenceType: values.recurrenceType,
      offerId: offer.id,
      venueId: offer.venue.id,
    })

    await onSubmit(values, departmentCode, offer.id, notify)

    await mutate(queryKeys, data, {
      revalidate: true,
    })
    await mutate([GET_OFFER_QUERY_KEY, offer.id])

    setIsDialogOpen(false)
  }

  const stocks = data?.stocks || []

  return (
    <>
      {mode !== OFFER_WIZARD_MODE.READ_ONLY && (
        //  When the mode is read only, the title is already inside the SummarySection layout
        <div className={styles['header']}>
          {timetableTypeRadioGroupShown ? (
            <h3 className={styles['subtitle']}>Dates et capacités</h3>
          ) : (
            <h2 className={styles['title']}>Dates et capacités</h2>
          )}
          {offer.hasStocks && !isOfferSynchronized(offer) && (
            <DialogBuilderButton
              triggerLabel="Ajouter une ou plusieurs dates"
              triggerVariant={ButtonVariant.SECONDARY}
              offer={offer}
              handleSubmitRecurrenceFormDrawer={
                handleSubmitRecurrenceFormDrawer
              }
              isDialogOpen={isDialogOpen}
              setIsDialogOpen={setIsDialogOpen}
            />
          )}
        </div>
      )}
      {isLoading && offer.hasStocks && (
        <Spinner className={styles['spinner']} />
      )}
      {!offer.hasStocks && (
        <div className={styles['no-stocks-content']}>
          {isOfferSynchronized(offer) ? (
            <p>Aucune date à afficher</p>
          ) : (
            <>
              <div className={styles['icon-container']}>
                <SvgIcon
                  alt=""
                  className={styles['icon']}
                  src={strokeAddCalendarIcon}
                />
              </div>
              <DialogBuilderButton
                triggerLabel="Définir le calendrier"
                triggerVariant={ButtonVariant.PRIMARY}
                offer={offer}
                handleSubmitRecurrenceFormDrawer={
                  handleSubmitRecurrenceFormDrawer
                }
                isDialogOpen={isDialogOpen}
                setIsDialogOpen={setIsDialogOpen}
              />
            </>
          )}
        </div>
      )}
      <div className={styles['container']}>
        {data?.hasStocks && !isLoading && (
          <div className={styles['content']}>
            <div className={styles['filters']}>
              <StocksCalendarFilters
                priceCategories={offer.priceCategories}
                filters={appliedFilters}
                sortType={appliedSort}
                onUpdateFilters={(filters) => {
                  //  Go back to the first page.
                  //  Because the current page may not exist anymore if there are less filtered dates than before
                  setPage(1)
                  setAppliedFilters(filters)
                }}
                onUpdateSort={(sort, desc) => {
                  setAppliedSort({
                    sort: sort ? sort : undefined,
                    orderByDesc: Boolean(desc),
                  })
                }}
                mode={mode}
              />
            </div>
            {data.stockCount > 0 && (
              <div className={styles['count']}>
                {pluralize(data.stockCount, 'date')}
              </div>
            )}
            <StocksCalendarTable
              stocks={stocks}
              offer={offer}
              onDeleteStocks={deleteStocks}
              checkedStocks={checkedStocks}
              updateCheckedStocks={setCheckedStocks}
              departmentCode={departmentCode}
              mode={mode}
              onUpdateStock={updateStock}
            />
            <div className={styles['pagination']}>
              <Pagination
                currentPage={page}
                onNextPageClick={() => setPage((p) => p + 1)}
                onPreviousPageClick={() => setPage((p) => p - 1)}
                pageCount={
                  data.stockCount % STOCKS_PER_PAGE === 0
                    ? data.stockCount / STOCKS_PER_PAGE
                    : Math.trunc(data.stockCount / STOCKS_PER_PAGE) + 1
                }
              />
            </div>
          </div>
        )}

        <StocksCalendarActionsBar
          checkedStocks={checkedStocks}
          hasStocks={Boolean(data?.hasStocks)}
          deleteStocks={deleteStocks}
          updateCheckedStocks={setCheckedStocks}
          mode={mode}
          offerId={offer.id}
        />
      </div>
    </>
  )
}

function DialogBuilderButton({
  triggerLabel,
  triggerVariant,
  isDialogOpen,
  setIsDialogOpen,
  offer,
  handleSubmitRecurrenceFormDrawer,
}: {
  triggerLabel: string
  triggerVariant: ButtonVariant
  isDialogOpen: boolean
  setIsDialogOpen: Dispatch<SetStateAction<boolean>>
  offer: GetIndividualOfferWithAddressResponseModel
  handleSubmitRecurrenceFormDrawer: (
    values: RecurrenceFormValues
  ) => Promise<void>
}) {
  return (
    <DialogBuilder
      trigger={
        <Button variant={triggerVariant} className={styles['button']}>
          {triggerLabel}
        </Button>
      }
      open={isDialogOpen}
      onOpenChange={setIsDialogOpen}
      variant="drawer"
      title={triggerLabel}
    >
      <RecurrenceForm
        priceCategories={offer.priceCategories ?? []}
        handleSubmit={handleSubmitRecurrenceFormDrawer}
      />
    </DialogBuilder>
  )
}
