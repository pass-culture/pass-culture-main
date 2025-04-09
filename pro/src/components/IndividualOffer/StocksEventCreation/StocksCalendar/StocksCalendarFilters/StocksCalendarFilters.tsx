import { StocksOrderedBy } from 'apiClient/v1'
import { PriceCategoryResponseModel } from 'apiClient/v1/models/PriceCategoryResponseModel'
import { getPriceCategoryOptions } from 'components/IndividualOffer/StocksEventEdition/getPriceCategoryOptions'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DatePicker } from 'ui-kit/formV2/DatePicker/DatePicker'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TimePicker } from 'ui-kit/formV2/TimePicker/TimePicker'

import { StocksTableFilters, StocksTableSort } from '../../form/types'

import styles from './StocksCalendarFilters.module.scss'

const stockTableSortTypes: {
  name: string
  sort: StocksOrderedBy
  orderByDesc: boolean
}[] = [
  { name: 'Date décroissante', sort: StocksOrderedBy.DATE, orderByDesc: true },
  { name: 'Date croissante', sort: StocksOrderedBy.DATE, orderByDesc: false },
  {
    name: 'Place décroissante',
    sort: StocksOrderedBy.DN_BOOKED_QUANTITY,
    orderByDesc: true,
  },
  {
    name: 'Place croissante',
    sort: StocksOrderedBy.DN_BOOKED_QUANTITY,
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

export const StocksCalendarFilters = ({
  priceCategories,
  filters,
  sortType,
  onUpdateFilters,
  onUpdateSort,
}: {
  priceCategories?: Array<PriceCategoryResponseModel> | null
  filters: StocksTableFilters
  sortType: StocksTableSort
  onUpdateFilters: (filters: StocksTableFilters) => void
  onUpdateSort: (sort?: StocksTableSort['sort'], orderByDesc?: boolean) => void
}) => {
  const hasFiltersApplied = Object.values(filters).some(Boolean)
  return (
    <div className={styles['container']}>
      <Select
        label="Trier par"
        name="sort"
        options={stockTableSortTypes.map((type) => ({
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
        options={getPriceCategoryOptions(priceCategories)}
        defaultOption={{ label: 'Tous les tarifs', value: '' }}
        value={filters.priceCategoryId || ''}
        onChange={(e) =>
          onUpdateFilters({ ...filters, priceCategoryId: e.target.value })
        }
      />
      {hasFiltersApplied && (
        <Button
          icon={fullRefreshIcon}
          onClick={() => onUpdateFilters({})}
          variant={ButtonVariant.TERNARY}
          className={styles['reset-button']}
        >
          Réinitialiser les filtres
        </Button>
      )}
    </div>
  )
}
