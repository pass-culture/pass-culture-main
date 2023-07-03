import React from 'react'
import { Link } from 'react-router-dom'

import { Audience } from 'core/shared/types'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './NoResults.module.scss'

interface NoResultsProps {
  resetFilters: () => void
  audience: Audience
}

const NoResults = ({ resetFilters, audience }: NoResultsProps): JSX.Element => (
  <div className={styles['search-no-results']}>
    <SvgIcon
      src={strokeSearchIcon}
      alt="Illustration de recherche"
      className={styles['search-no-results-icon']}
      width="124"
    />
    <p className={styles['search-no-results-text']}>
      Aucune offre trouvée pour votre recherche
    </p>
    <p className={styles['search-no-results-text']}>
      Vous pouvez modifer votre recherche ou
      <br />
      <Link
        className="reset-filters-link"
        onClick={resetFilters}
        to={`/offres${audience === Audience.COLLECTIVE ? '/collectives' : ''}`}
      >
        afficher toutes les offres
      </Link>
    </p>
  </div>
)

export default NoResults
