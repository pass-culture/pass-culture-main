import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'

import { distanceOptions, INFINITE_DISTANCE } from './helpers'

class FilterByDistance extends PureComponent {
  handleOnChangeDistance = event => {
    const { filterActions, geolocation } = this.props
    const distance = event.target.value
    let { latitude, longitude } = geolocation

    if (distance === INFINITE_DISTANCE) {
      latitude = null
      longitude = null
    }

    filterActions.change({ distance, latitude, longitude })
  }

  render() {
    const { filterState, geolocation } = this.props
    const geolocationActive = geolocation.latitude != null && geolocation.longitude != null
    const distanceValue = filterState.params.distance || INFINITE_DISTANCE

    return (
      <Fragment>
        <div
          className="distance-filter-options"
          id="filter-by-distance"
        >
          <h2 className="distance-filter-title">{'Où'}</h2>
          {!geolocationActive && (
            <div className="geoloc-warning">
              {'Activez votre géolocalisation pour utiliser ce filtre.'}
            </div>
          )}
          <select
            className="pc-selectbox pl24 py5 fs19"
            defaultValue={distanceValue}
            disabled={!geolocationActive}
            name="distance"
            onBlur={this.handleOnChangeDistance}
          >
            {distanceOptions.map(({ label, value }) => (
              <option
                key={value}
                value={value}
              >
                {label}
              </option>
            ))}
          </select>
        </div>
        <hr className="dotted-bottom-primary" />
      </Fragment>
    )
  }
}

FilterByDistance.propTypes = {
  filterActions: PropTypes.shape({
    add: PropTypes.func.isRequired,
    change: PropTypes.func.isRequired,
    remove: PropTypes.func.isRequired,
  }).isRequired,
  filterState: PropTypes.shape({
    isNew: PropTypes.bool,
    params: PropTypes.shape({
      categories: PropTypes.string,
      date: PropTypes.string,
      distance: PropTypes.string,
      jours: PropTypes.string,
      latitude: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      longitude: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      'mots-cles': PropTypes.string,
      orderBy: PropTypes.string,
    }),
  }).isRequired,
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
    watchId: PropTypes.number,
  }).isRequired,
}

export default FilterByDistance
