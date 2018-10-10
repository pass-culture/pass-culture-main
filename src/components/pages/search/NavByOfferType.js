import PropTypes from 'prop-types'
import React from 'react'

import SearchPicture from './SearchPicture'

const NavByOfferType = ({ pagination, title, typeSublabels }) => (
  <div id="nav-by-offer-type">
    <h2 className="is-italic fs18">
      {title}
    </h2>
    <div className="list flex-columns wrap-2">
      {typeSublabels.map(typeSublabel => (
        <button
          key={typeSublabel}
          onClick={() =>
            pagination.change(
              { categories: typeSublabel },
              { pathname: `/recherche/resultats/${typeSublabel}` }
            )
          }
          type="button"
          className="item no-border no-background no-outline mt22 col-1of2"
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

export default NavByOfferType
