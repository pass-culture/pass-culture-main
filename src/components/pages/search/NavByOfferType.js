import PropTypes from 'prop-types'
import React from 'react'

import SearchPicture from './SearchPicture'
import { withQueryRouter } from '../../hocs/withQueryRouter'

const NavByOfferType = ({ pagination, title, typeSublabels }) => (
  <div id="nav-by-offer-type">
    <h2 className="is-italic fs15">
      {title}
    </h2>
    <div className="pc-list flex-columns wrap-2">
      {typeSublabels.map(typeSublabel => (
        <button
          id="button-nav-by-offer-type"
          key={typeSublabel}
          onClick={() =>
            pagination.change(
              { categories: typeSublabel, page: null },
              { pathname: `/recherche/resultats/${typeSublabel}` }
            )
          }
          type="button"
          className="item no-border no-background no-outline mt12 col-1of2"
        >
          <SearchPicture searchType={typeSublabel} />
        </button>
      ))}
    </div>
  </div>
)

NavByOfferType.propTypes = {
  pagination: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  typeSublabels: PropTypes.array.isRequired,
}

export default withQueryRouter(NavByOfferType)
