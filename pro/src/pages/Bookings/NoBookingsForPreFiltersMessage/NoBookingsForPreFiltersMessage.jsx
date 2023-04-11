import PropTypes from 'prop-types'
import React from 'react'

import './NoBookingsForPreFiltersMessage.scss'

import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import { Button } from 'ui-kit'
import Icon from 'ui-kit/Icon/Icon'

const NoBookingsForPreFiltersMessage = ({ resetPreFilters }) => (
  <div className="br-warning no-bookings-for-pre-filters">
    <Icon svg="ico-search-gray" />
    <strong>Aucune réservation trouvée pour votre recherche</strong>
    <p>
      {'Vous pouvez modifier vos filtres et lancer une nouvelle recherche ou '}
    </p>
    <Button
      Icon={ResetIcon}
      className="reset-filters-reservation-link-icon"
      onClick={resetPreFilters}
      variant="quaternary"
    >
      Réinitialiser les filtres
    </Button>
  </div>
)

NoBookingsForPreFiltersMessage.propTypes = {
  resetPreFilters: PropTypes.func.isRequired,
}

export default NoBookingsForPreFiltersMessage
