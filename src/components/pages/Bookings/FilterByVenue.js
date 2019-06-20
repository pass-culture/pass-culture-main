import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'

export class FilterByVenue extends PureComponent {
  componentDidMount() {
    this.props.loadVenues()
  }

  onChangeVenue = event => {
    const selectedVenue = document.getElementById("venues")
    const venueId = selectedVenue[selectedVenue.selectedIndex].value

    this.props.selectBookingsForVenues(venueId)
  }

  render() {
    const { venuesOptions, isDigital } = this.props
    const labelClassName = this.props.isDigital ?  "has-text-grey" :  "has-text-black"

    return (
      <Fragment>
        <div id="filter-by-venue">
          <label htmlFor="venues" className={labelClassName} >
            {"Choisissez un lieu dans la liste."}
          </label>
          <select
            id="venues"
            className="pc-selectbox pl24 py5 fs19"
            onChange={this.onChangeVenue}
            disabled={isDigital}
          >
            <option value="" disabled selected>Choisissez un lieu dans la liste.</option>
            {venuesOptions.map(({ name, id }) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}

          </select>
        </div>
        <div>
          {'ou :'}
        </div>
        <div className="select-digital-offer">
          <input
            id="isDigital"
            type="checkbox"
            onChange={() => document.getElementById("venues").value = ''}
            onClick={() => this.props.selectOnlyDigitalVenues(!isDigital)}
            defaultChecked={isDigital}
          />
          <label htmlFor="isDigital">
            {"Cocher cette case pour voir les offres numériques."}
          </label>
        </div>
      </Fragment>
    )
  }
}

FilterByVenue.defaultProps = {
  venuesOptions: [],
}

FilterByVenue.propTypes = {
  isDigital: PropTypes.bool.isRequired,
  loadVenues: PropTypes.func.isRequired,
  venueId: PropTypes.string,
  venuesOptions: PropTypes.array.isRequired,
}
