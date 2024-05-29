import React from 'react'

import fullRefresh from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoBookingsForPreFiltersMessage.module.scss'

interface NoBookingsForPreFiltersMessageProps {
  resetPreFilters: () => void
}

export const NoBookingsForPreFiltersMessage = ({
  resetPreFilters,
}: NoBookingsForPreFiltersMessageProps): JSX.Element => (
  <div className={styles['search-no-results']}>
    <SvgIcon
      src={strokeSearchIcon}
      alt=""
      className={styles['search-no-results-icon']}
      width="124"
    />
    <p className={styles['search-no-results-title4']}>
      Aucune réservation trouvée pour votre recherche
    </p>
    <p className={styles['search-no-results-text']}>
      Vous pouvez modifier vos filtres et lancer une nouvelle recherche ou
    </p>
    <Button
      variant={ButtonVariant.TERNARYPINK}
      icon={fullRefresh}
      onClick={resetPreFilters}
    >
      Afficher toutes les réservations
    </Button>
  </div>
)
