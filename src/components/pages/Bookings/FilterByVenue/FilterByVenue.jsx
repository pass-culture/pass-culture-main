import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'

class FilterByVenue extends PureComponent {
  componentDidMount() {
    const { loadVenues, isUserAdmin, notification, showNotification } = this.props
    if (!notification && isUserAdmin) {
      showNotification()
    }
    loadVenues()
  }

  componentWillUnmount() {
    const { closeNotification, notification } = this.props
    if (notification && notification.tag === 'admin-bookings-access') {
      closeNotification()
    }
  }

  handleOnClick = () => {
    const { isDigital, updateIsFilteredByDigitalVenues } = this.props
    updateIsFilteredByDigitalVenues(!isDigital)
  }

  render() {
    const { isDigital, updateVenueId, venueId, venuesOptions } = this.props
    const labelClassName = isDigital ? 'has-text-grey' : 'has-text-black'

    return (
      <Fragment>
        <div id="filter-by-venue">
          <label
            className={labelClassName}
            htmlFor="venues"
          >
            {'Sélectionner le lieu qui accueille l’offre : '}
          </label>
          <select
            className="pc-selectbox"
            disabled={isDigital}
            id="venues"
            onBlur={updateVenueId}
            onChange={updateVenueId}
            value={venueId}
          >
            <option
              disabled
              label=" - Choisissez un lieu dans la liste - "
              selected
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
          <div>
            {'ou :'}
          </div>
          <input
            className="pc-checkbox input"
            defaultChecked={isDigital}
            id="isDigital"
            onClick={this.handleOnClick}
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
  notification: null,
  venueId: '',
}

FilterByVenue.propTypes = {
  closeNotification: PropTypes.func.isRequired,
  isDigital: PropTypes.bool.isRequired,
  isUserAdmin: PropTypes.bool.isRequired,
  loadVenues: PropTypes.func.isRequired,
  notification: PropTypes.shape(),
  showNotification: PropTypes.func.isRequired,
  updateIsFilteredByDigitalVenues: PropTypes.func.isRequired,
  updateVenueId: PropTypes.func.isRequired,
  venueId: PropTypes.string,
  venuesOptions: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default FilterByVenue
