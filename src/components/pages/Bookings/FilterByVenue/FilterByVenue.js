import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'

class FilterByVenue extends PureComponent {
  componentDidMount() {
    const { loadVenues } = this.props
    loadVenues()
  }

  handleOnClick = () => () => {
    const { isDigital, selectOnlyDigitalVenues } = this.props
    selectOnlyDigitalVenues(!isDigital)
  }

  render() {
    const { venuesOptions, isDigital, selectBookingsForVenues, venueId } = this.props
    const labelClassName = isDigital
      ? 'has-text-grey'
      : 'has-text-black'

    return (
      <Fragment>
        <div id="filter-by-venue">
          <label
            className={labelClassName}
            htmlFor="venues"
          >
            {'Sélectionnez un lieu :'}
          </label>
          <select
            className="pc-selectbox pl24 py5 fs19"
            disabled={isDigital}
            id="venues"
            onChange={selectBookingsForVenues}
            value={venueId}
          >
            <option
              disabled
              label=" "
            />
            {venuesOptions.map(({ name, id }) => (
              <option
                key={id}
                value={id}
              >
                {name}
              </option>
            ))}
          </select>
        </div>
        <div className="select-digital-offer mt16 mb12">
          <div>{'ou :'}</div>
          <input
            className="pc-checkbox input"
            defaultChecked={isDigital}
            id="isDigital"
            onClick={this.handleOnClick()}
            type="checkbox"
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
  selectBookingsForVenues: PropTypes.func.isRequired,
  selectOnlyDigitalVenues: PropTypes.func.isRequired,
  venueId: PropTypes.string,
  venuesOptions: PropTypes.arrayOf.isRequired,
}

export default FilterByVenue
