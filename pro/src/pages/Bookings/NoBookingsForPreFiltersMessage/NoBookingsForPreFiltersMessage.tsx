import React from 'react'

import fullRefresh from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoBookingsForPreFiltersMessage.module.scss'

interface NoBookingsForPreFiltersMessageProps {
  resetPreFilters: () => void
}

const NoBookingsForPreFiltersMessage = ({
  resetPreFilters,
}: NoBookingsForPreFiltersMessageProps) => (
  <div className={styles['search-no-results']}>
    <SvgIcon
      src={strokeSearchIcon}
      alt=""
      width="124"
      className={styles['search-no-results-icon']}
    />
    <p className={styles['search-no-results-title4']}>
      Aucune réservation trouvée pour votre recherche
    </p>
    <p className={styles['search-no-results-text']}>
      Vous pouvez modifier vos filtres et lancer une nouvelle recherche ou
    </p>
    <Button
      className={styles['reset-filters-link']}
      onClick={resetPreFilters}
      type="button"
      variant={ButtonVariant.TERNARYPINK}
      icon={fullRefresh}
    >
      Réinitialiser les filtres
    </Button>
  </div>
)

export default NoBookingsForPreFiltersMessage
