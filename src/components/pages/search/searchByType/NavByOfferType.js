import PropTypes from 'prop-types'
import React from 'react'
import kebabcase from 'lodash.kebabcase'

import { SearchPicture } from '../SearchPicture'

const NavByOfferType = ({
  title,
  typeSublabels,
  resetSearchStore,
  updateSearchQuery,
}) => (
  <div id="nav-by-offer-type">
    <h2 className="is-italic fs15">{title}</h2>
    <div className="pc-list flex-columns wrap-2">
      {typeSublabels.map(typeSublabel => (
        <button
          id={`button-nav-by-offer-type-${kebabcase(typeSublabel)}`}
          key={typeSublabel}
          onClick={() => {
            resetSearchStore()
            updateSearchQuery(typeSublabel)
          }}
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
  resetSearchStore: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  typeSublabels: PropTypes.array.isRequired,
  updateSearchQuery: PropTypes.func.isRequired,
}

export default NavByOfferType
