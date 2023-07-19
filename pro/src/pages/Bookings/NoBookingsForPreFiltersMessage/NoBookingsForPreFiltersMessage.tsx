import React from 'react'

import './NoBookingsForPreFiltersMessage.scss'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

interface NoBookingsForPreFiltersMessageProps {
  resetPreFilters: () => void
}

const NoBookingsForPreFiltersMessage = ({
  resetPreFilters,
}: NoBookingsForPreFiltersMessageProps) => (
  <div className="br-warning no-bookings-for-pre-filters">
    <SvgIcon
      src={strokeSearchIcon}
      alt=""
      width="124"
      className="stroke-search-icon"
    />
    <p>Aucune réservation trouvée pour votre recherche</p>
    <p>
      {'Vous pouvez modifier vos filtres et lancer une nouvelle recherche ou '}
      <button
        className="tertiary-button reset-filters-link"
        onClick={resetPreFilters}
        type="button"
      >
        réinitialiser les filtres
      </button>
    </p>
  </div>
)

export default NoBookingsForPreFiltersMessage
