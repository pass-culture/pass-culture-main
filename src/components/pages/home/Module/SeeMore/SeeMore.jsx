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

const noOp = () => false

const preventDefault = event => {
  event.preventDefault()
}

const SeeMore = ({ historyPush, isSwitching, layout, parameters }) => {
  function goToSearchPage(event) {
    if (!isSwitching) {
      historyPush({
        pathname: '/recherche/resultats',
        parametersFromHome: parameters,
        search: buildSearchParameters(parameters),
      })
    }
    event.preventDefault()
  }

  return (
    <li
      className="see-more-wrapper"
      key='see-more'
    >
      <Link
        onClick={goToSearchPage}
        onMouseDown={preventDefault}
        to={noOp}
      >
        <div className={`smw-image-${layout}`}>
          <div className="smw-content-wrapper">
            <Icon
              className="smw-icon-wrapper"
              svg={`${layout === PANE_LAYOUT['ONE-ITEM-MEDIUM'] ? 'ico-offres-home-white' : 'ico-offres-home-purple'}`}
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
  historyPush: PropTypes.func.isRequired,
  isSwitching: PropTypes.bool.isRequired,
  layout: PropTypes.string,
  parameters: PropTypes.shape().isRequired,
}

export default SeeMore
