import { StocksOrderedBy } from '@/apiClient/v1'
import type { PriceCategoryResponseModel } from '@/apiClient/v1/models/PriceCategoryResponseModel'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { useIsCaledonian } from '@/commons/hooks/useIsCaledonian'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { getPriceCategoryOptions } from '@/pages/IndividualOffer/commons/getPriceCategoryOptions'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { Select } from '@/ui-kit/form/Select/Select'
import { TimePicker } from '@/ui-kit/form/TimePicker/TimePicker'

import type { StocksTableFilters, StocksTableSort } from '../form/types'
import styles from './StocksCalendarFilters.module.scss'

export type StocksCalendarFiltersProps = {
  priceCategories?: Array<PriceCategoryResponseModel> | null
  filters: StocksTableFilters
  sortType: StocksTableSort
  onUpdateFilters: (filters: StocksTableFilters) => void
  onUpdateSort: (sort?: StocksTableSort['sort'], orderByDesc?: boolean) => void
  mode: OFFER_WIZARD_MODE
}

function getStockTableSortTypes(mode: OFFER_WIZARD_MODE): {
  name: string
  sort: StocksOrderedBy
  orderByDesc: boolean
}[] {
  const remainlingQuantityLabel =
    mode === OFFER_WIZARD_MODE.CREATION ? 'Place' : 'Quantité'

  return [
    {
      name: 'Date décroissante',
      sort: StocksOrderedBy.DATE,
      orderByDesc: true,
    },
    { name: 'Date croissante', sort: StocksOrderedBy.DATE, orderByDesc: false },
    {
      name: `${remainlingQuantityLabel} décroissante`,
      sort: StocksOrderedBy.REMAINING_QUANTITY,
      orderByDesc: true,
    },
    {
      name: `${remainlingQuantityLabel} croissante`,
      sort: StocksOrderedBy.REMAINING_QUANTITY,
      orderByDesc: false,
    },
    {
      name: 'Date limite de réservation décroissante',
      sort: StocksOrderedBy.BOOKING_LIMIT_DATETIME,
      orderByDesc: true,
    },
    {
      name: 'Date limite de réservation croissante',
      sort: StocksOrderedBy.BOOKING_LIMIT_DATETIME,
      orderByDesc: false,
    },
  ]
}

export const StocksCalendarFilters = ({
  priceCategories,
  filters,
  sortType,
  onUpdateFilters,
  onUpdateSort,
  mode,
}: StocksCalendarFiltersProps) => {
  const isCaledonian = useIsCaledonian()

  const hasFiltersApplied = Object.values(filters).some(Boolean)
  return (
    <div className={styles['container']}>
      <Select
        label="Trier par"
        name="sort"
        options={getStockTableSortTypes(mode).map((type) => ({
          label: type.name,
          value: `${type.sort}${type.orderByDesc ? ' desc' : ''}`,
        }))}
        value={`${sortType.sort || ''}${sortType.orderByDesc ? ' desc' : ''}`}
        onChange={(e) => {
          const [sort, orderByDesc] = e.target.value.split(' ')
          onUpdateSort(sort as StocksTableSort['sort'], orderByDesc === 'desc')
        }}
        defaultOption={{ label: 'Aucun tri', value: '' }}
        className={styles['sort-select']}
      />
      <div className={styles['separator']}></div>
      <DatePicker
        label="Date"
        name="date"
        value={filters.date || ''}
        onChange={(e) => onUpdateFilters({ ...filters, date: e.target.value })}
      />
      <TimePicker
        label="Horaire"
        name="time"
        className={styles['time-picker']}
        value={filters.time || ''}
        onChange={(e) => onUpdateFilters({ ...filters, time: e.target.value })}
      />
      <Select
        label="Tarif"
        className={styles['place-category-select']}
        name="price-category"
        options={getPriceCategoryOptions(priceCategories, isCaledonian)}
        defaultOption={{ label: 'Tous les tarifs', value: '' }}
        value={filters.priceCategoryId || ''}
        onChange={(e) =>
          onUpdateFilters({ ...filters, priceCategoryId: e.target.value })
        }
      />
      <div className={styles['filter-reset']}>
        <Button
          icon={fullRefreshIcon}
          onClick={() => onUpdateFilters({})}
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          label="Réinitialiser les filtres"
          disabled={!hasFiltersApplied}
        />
      </div>
    </div>
  )
}
