import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'

import styles from './NoResults.module.scss'

interface INoResultsProps {
  resetFilters: () => void
}

const NoResults = ({ resetFilters }: INoResultsProps): JSX.Element => (
  <div className={styles['search-no-results']}>
    <Icon
      alt="Illustration de recherche"
      className={styles['search-no-results-icon']}
      svg="ico-search-gray"
    />
    <p className={styles['search-no-results-text']}>
      Aucune offre trouvée pour votre recherche
    </p>
    <p className={styles['search-no-results-text']}>
      Vous pouvez modifer votre recherche ou
      <br />
      <Link className="reset-filters-link" onClick={resetFilters} to="/offres">
        afficher toutes les offres
      </Link>
    </p>
  </div>
)

export default NoResults
