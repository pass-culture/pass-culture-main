import React, { PureComponent, Fragment } from 'react'
import PropTypes from 'prop-types'

export class FilterByVenue extends PureComponent {
  constructor() {
    super()
    this.state = {
      isDigital: false,
      venueID: null,
    }
    this.handleIsDigitalChecked = this.handleIsDigitalChecked.bind(this)
  }

  handleIsDigitalChecked = event => {
    const isDigital = document.getElementById("isDigital").checked
    const labelClassName = isDigital ?  "has-text-grey" :  "has-text-black"
    this.setState({isDigital, labelClassName })
  }

  onChangeVenue = event => {
    const selectedVenue = document.getElementById("venues")
    const venueId = selectedVenue[selectedVenue.selectedIndex].value
    this.setState({venueId })
  }

  render() {
    const { venuesOptions } = this.props
    const {labelClassName, isDigital} = this.state

    return (
      <Fragment>
        <div id="filter-by-venue">
          <label htmlFor="venues" className={labelClassName} >
            {"Sélectionner le lieu qui acceuille l'offre :"}
          </label>
          <select
            id="venues"
            className="pc-selectbox pl24 py5 fs19"
            defaultValue="all"
            onChange={this.onChangeVenue}
            disabled={isDigital}
          >
            {venuesOptions.map(({ name, id }) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <div className="field-group">
          <div>
            {'ou :'}
          </div>
          <label htmlFor="isDigital">
            {"Cocher cette case pour voir les offres numériques"}
          </label>
          <input
            id="isDigital"
            type="checkbox"
            onClick={this.handleIsDigitalChecked}
          />
        </div>
      </Fragment>
    )
  }
}

FilterByVenue.defaultProps = {
  venuesOptions: [],
}

FilterByVenue.propTypes = {
  venuesOptions: PropTypes.array.isRequired,
}
