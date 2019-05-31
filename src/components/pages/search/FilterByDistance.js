import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import options, {
  INFINITE_DISTANCE,
} from '../../../helpers/search/distanceOptions'

class FilterByDistance extends Component {
  onChangeDistance = event => {
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
    const { filterState, title } = this.props

    // https://stackoverflow.com/questions/37946229/how-do-i-reset-the-defaultvalue-for-a-react-input
    // WE NEED TO MAKE THE PARENT OF THE KEYWORD INPUT
    // DEPENDING ON THE KEYWORDS VALUE IN ORDER TO RERENDER
    // THE IN PUT WITH A SYNCED DEFAULT VALUE
    const distanceKey =
      filterState.params.distance === null ? 'empty' : 'not-empty'
    const distanceValue = filterState.params.distance || 20000

    return (
      <React.Fragment>
        <div
          key={distanceKey}
          id="filter-by-distance"
          className="pt18 text-center mb20"
        >
          <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">
            {title}
          </h2>
          <select
            className="pc-selectbox pl24 py5 fs19"
            defaultValue={distanceValue}
            onChange={this.onChangeDistance}
          >
            {options.map(({ label, value }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <hr className="dotted-bottom-primary" />
      </React.Fragment>
    )
  }
}

FilterByDistance.propTypes = {
  filterActions: PropTypes.object.isRequired,
  filterState: PropTypes.object.isRequired,
  geolocation: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
}

const mapStateToProps = state => ({
  geolocation: state.geolocation,
})

export default connect(mapStateToProps)(FilterByDistance)
