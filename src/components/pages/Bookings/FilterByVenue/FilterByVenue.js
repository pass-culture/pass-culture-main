import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'

class FilterByVenue extends PureComponent {
  componentDidMount() {
    const { loadVenues } = this.props
    loadVenues()
  }

  render() {
    const { venuesOptions, isDigital, selectBookingsForVenues, venueId } = this.props
    const labelClassName = this.props.isDigital
      ? 'has-text-grey'
      : 'has-text-black'

    return (
      <Fragment>
        <div id="filter-by-venue">
          <label htmlFor="venues" className={labelClassName}>
            {'Sélectionnez un lieu :'}
          </label>
          <select
            id="venues"
            className="pc-selectbox pl24 py5 fs19"
            onChange={selectBookingsForVenues}
            value={venueId}
            disabled={isDigital}>
            <option disabled label=" "></option>
            {venuesOptions.map(({ name, id }) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <div className="select-digital-offer mt16 mb12">
          <div>{'ou :'}</div>
          <input
            id="isDigital"
            className="pc-checkbox input"
            type="checkbox"
            onClick={() => this.props.selectOnlyDigitalVenues(!isDigital)}
            defaultChecked={isDigital}
          />
          <label htmlFor="isDigital">
            {'Cochez cette case pour voir les offres numériques'}
          </label>
        </div>
      </Fragment>
    )
  }
}

FilterByVenue.defaultProps = {
  venueId: '',
}

FilterByVenue.propTypes = {
  isDigital: PropTypes.bool.isRequired,
  loadVenues: PropTypes.func.isRequired,
  venueId: PropTypes.string,
  venuesOptions: PropTypes.array.isRequired,
}

export default FilterByVenue
