import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import {Field, Form} from 'pass-culture-shared';

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

    var isDigitalChecked = document.getElementById("isDigital").checked
    var selectVenue = document.getElementById('venues')
    selectVenue.disabled = isDigitalChecked
    this.setState({isDigital: isDigitalChecked })
    const { checked } = this.props
    console.log("isDigitalChecked", isDigitalChecked)
    console.log("checked", checked)
  }

  onChangeVenue = event => {
    const selectedVenue = document.getElementById("venues")
    const venueId = selectedVenue[selectedVenue.selectedIndex].value
    this.setState({venueId: venueId })
    console.log("venueId", venueId)
  }

  render() {
    const { venuesOptions } = this.props
    const {isDigital} = this.state
    console.log(this.state.isDigital)
    const venueSelectionIsDisabled=isDigital

    return (
      <React.Fragment>
        <h2 disabled={venueSelectionIsDisabled}>
          {'Sélectionner le lieu qui acceuille l\'offre :'}
        </h2>
        <div id="filter-by-venue">
          <select
            disabled={venueSelectionIsDisabled}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue="all"
            id="venues"
            onChange={this.onChangeVenue}
          >
            {venuesOptions.map(({ name, id }) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <hr className="dotted-bottom-primary" />
        <Form
          action="/bookings"
          name="digitalOffer"
          Tag={null}>
          <h2>
            {'ou :'}
          </h2>
          <div className="field-group">
            <Field
              id="isDigital"
              name="isDigital"
              type="checkbox"
              label="Cocher cette case pour voir les offres numériques"
              checked={this.state.isDigital}
              onChange={this.handleIsDigitalChecked}
            />
          </div>
        </Form>
      </React.Fragment>
    )

  }
}

FilterByVenue.propTypes = {
  venuesOptions: PropTypes.array.isRequired,
}
