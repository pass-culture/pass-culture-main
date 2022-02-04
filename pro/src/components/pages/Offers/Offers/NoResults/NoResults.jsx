import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'

const NoResults = ({ resetFilters }) => (
  <div className="search-no-results">
    <Icon alt="Illustration de recherche" svg="ico-search-gray" />
    <p>Aucune offre trouvée pour votre recherche</p>
    <p>
      Vous pouvez modifer votre recherche ou
      <br />
      <Link className="reset-filters-link" onClick={resetFilters} to="/offres">
        afficher toutes les offres
      </Link>
    </p>
  </div>
)

NoResults.propTypes = {
  resetFilters: PropTypes.func.isRequired,
}

export default NoResults
