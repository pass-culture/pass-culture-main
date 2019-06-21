import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'

import {FilterByVenue} from './FilterByVenue'
import FilterByDateContainer from './FilterByDateContainer'

export class FilterByOffer extends PureComponent {

  componentDidMount() {
    this.props.loadOffers()
  }

  onChangeOffer = event => {
    const selectedOffer = document.getElementById("offers")
    const offerId = selectedOffer[selectedOffer.selectedIndex].value
    this.props.selectBookingsForOffers(offerId)
  }

  render() {
    const { offersOptions, isFilterByDigitalVenues, venueId } = this.props

    if ((venueId !== "" && !isFilterByDigitalVenues) || isFilterByDigitalVenues) {
      return (
        <React.Fragment>
          <div id="filter-by-offer">
            <div className="section">
              <h2 className="main-list-title">
                {isFilterByDigitalVenues ? 'OFFRE NUMERIQUE' : 'OFFRE'}
              </h2>
              <div>
                Télécharger les réservations pour l'offre {isFilterByDigitalVenues ? 'numérique' : ''} :
              </div>
              <select
                id="offers"
                className="pc-selectbox pl24 py5 fs19"
                onChange={this.onChangeOffer}
                defaultValue=""
              >
                <option value="">Choisissez une offre dans la liste.</option>
                <option value="all">Toutes les offres</option>
              }
                {offersOptions.map(({name, id}) => (
                  <option key={id} value={id}>
                    {name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <FilterByDateContainer
          />
        </React.Fragment>
      )
    }

    return null

  }
}

FilterByVenue.defaultProps = {
  offersOptions: [],
}

FilterByOffer.propTypes = {
  offersOptions: PropTypes.array.isRequired,
  isFilterByDigitalVenues: PropTypes.bool.isRequired,
  loadOffers: PropTypes.func.isRequired,
  offerId: PropTypes.string,
  venueId: PropTypes.string,
}
