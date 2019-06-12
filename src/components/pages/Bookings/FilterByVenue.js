import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

export class FilterByVenue extends PureComponent {
  constructor() {
    super()
    this.state = {venueID: null}
  }

  onChangeVenue = event => {
    const selectedVenue = document.getElementById("venues")
    const venueId = selectedVenue[selectedVenue.selectedIndex].value
    this.setState({venueId: venueId })
    console.log("venueId", venueId)
  }

  render() {
    const { venues } = this.props
    const isDisabled=false

    return (
      <React.Fragment>
        <h2 disabled={isDisabled}>
          {'Sélectionner le lieu qui acceuille l\'offre :'}
        </h2>
        <div id="filter-by-venue">
          <select
            disabled={isDisabled}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue="all"
            id="venues"
            onChange={this.onChangeVenue}
          >
            {venues.map(({ name, id }) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <hr className="dotted-bottom-primary" />
      </React.Fragment>
    )

  }
}

FilterByVenue.propTypes = {
  venues: PropTypes.array.isRequired,
}
