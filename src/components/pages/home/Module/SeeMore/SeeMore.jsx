import PropTypes from 'prop-types'
import React from 'react'
import Icon from '../../../../layout/Icon/Icon'
import { PANE_LAYOUT } from '../../domain/layout'
import { Link } from 'react-router-dom'

const buildSearchParameters = parameters => {
  const { geolocation, offerCategories, searchAround } = parameters

  let search = `?autour-de=${searchAround ? 'oui' : 'non'}`
  if (offerCategories.length > 0) {
    search = search.concat(`&categories=${offerCategories.join(';')}`)
  }
  if (geolocation && geolocation.latitude && geolocation.longitude) {
    search = search.concat(`&latitude=${geolocation.latitude}&longitude=${geolocation.longitude}`)
  }
  return search
}

const SeeMore = ({ layout, parameters }) => {
  return (
    <li
      className="see-more-wrapper"
      key='see-more'
    >
      <Link to={{
        pathname: '/recherche/resultats',
        parametersFromHome: parameters,
        search: buildSearchParameters(parameters),
      }}
      >
        <div className={`smw-image-${layout}`}>
          <div className="smw-content-wrapper">
            <Icon
              className="smw-icon-wrapper"
              svg="ico-offres-home-white"
            />
            <span>
              {'En voir plus'}
            </span>
          </div>
        </div>
      </Link>
    </li>
  )
}

SeeMore.defaultProps = {
  layout: PANE_LAYOUT['ONE-ITEM-MEDIUM'],
}

SeeMore.propTypes = {
  layout: PropTypes.string,
  parameters: PropTypes.shape().isRequired,
}

export default SeeMore
