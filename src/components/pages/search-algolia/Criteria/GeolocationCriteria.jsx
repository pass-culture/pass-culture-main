import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import Header from '../../../layout/Header/Header'
import Icon from '../../../layout/Icon/Icon'
import { GEOLOCATION_CRITERIA } from './geolocationCriteriaValues'

class GeolocationCriteria extends PureComponent {
  handleCriterionSelection = criterionKey => () => {
    const { onGeolocationCriterionSelection, isGeolocationEnabled } = this.props
    if (GEOLOCATION_CRITERIA[criterionKey].requiresGeolocation && !isGeolocationEnabled()) {
      return window.alert(
        'Veuillez activer la géolocalisation pour voir les offres autour de vous.'
      )
    }
    onGeolocationCriterionSelection(criterionKey)
  }

  render() {
    const { location, match, history, activeGeolocationLabel } = this.props
    return (
      <div>
        <Header
          backTo="/recherche-offres"
          closeTo=""
          extraClassName="gc-header"
          history={history}
          location={location}
          match={match}
          title="Localisation"
        />
        <ul className="gc-item-list">
          {Object.keys(GEOLOCATION_CRITERIA).map(criterionKey => {
            const label = GEOLOCATION_CRITERIA[criterionKey].label
            const icon = GEOLOCATION_CRITERIA[criterionKey].icon
            const isActive = activeGeolocationLabel === label
            return (
              <li key={label}>
                <button
                  className="gc-item"
                  onClick={this.handleCriterionSelection(criterionKey)}
                  type="button"
                >
                  <div className={`gc-item-icon-bg ${isActive && 'gc-active-icon'}`}>
                    <Icon
                      className="gc-item-icon"
                      svg={icon}
                    />
                  </div>
                  <span className={`gc-item-label ${isActive && 'gc-active-label'}`}>
                    {label}
                  </span>
                  {isActive && <Icon
                    className="gc-item-icon-check"
                    svg="ico-check-pink"
                               />}
                </button>
              </li>
            )
          })}
        </ul>
      </div>
    )
  }
}

GeolocationCriteria.propTypes = {
  activeGeolocationLabel: PropTypes.string.isRequired,
  history: PropTypes.shape({
    replace: PropTypes.func.isRequired,
    push: PropTypes.func.isRequired,
  }).isRequired,
  isGeolocationEnabled: PropTypes.func.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  onGeolocationCriterionSelection: PropTypes.func.isRequired,
}

export default GeolocationCriteria
