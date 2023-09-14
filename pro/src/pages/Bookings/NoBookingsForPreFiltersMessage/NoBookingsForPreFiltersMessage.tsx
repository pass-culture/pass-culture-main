import React from 'react'

import { Audience } from 'core/shared/types'
import fullRefresh from 'icons/full-refresh.svg'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { ButtonLink } from 'ui-kit/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoBookingsForPreFiltersMessage.module.scss'
interface NoBookingsForPreFiltersMessageProps {
  resetPreFilters: () => void
  audience: Audience
}

const NoBookingsForPreFiltersMessage = ({
  resetPreFilters,
  audience,
}: NoBookingsForPreFiltersMessageProps): JSX.Element => (
  <div className={styles['search-no-results']}>
    <SvgIcon
      src={strokeSearchIcon}
      alt="Illustration de recherche"
      className={styles['search-no-results-icon']}
      width="124"
    />
    <p className={styles['search-no-results-title4']}>
      Aucune réservation trouvée pour votre recherche
    </p>
    <p className={styles['search-no-results-text']}>
      Vous pouvez modifier vos filters et lancer une nouvelle recherche ou
    </p>
    <ButtonLink
      variant={ButtonVariant.TERNARYPINK}
      icon={fullRefresh}
      link={{
        to: `/reservations${
          audience === Audience.COLLECTIVE ? '/collectives' : ''
        }`,
        isExternal: false,
      }}
      onClick={resetPreFilters}
    >
      Réinitialiser les filtres
    </ButtonLink>
  </div>
)

export default NoBookingsForPreFiltersMessage
