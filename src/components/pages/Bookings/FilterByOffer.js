import React, { PureComponent } from 'react'
import classnames from 'classnames'
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

  onChangeDigitalOffer = event => {
    const selectedDigitalOffer = document.getElementById("digitalOffers")
    const digitalOfferId = selectedDigitalOffer[selectedDigitalOffer.selectedIndex].value
    console.log("digitalOfferId", digitalOfferId)
    this.props.selectBookingsForOffers(digitalOfferId)
  }


  render() {
    const { offersOptions, isFilterByDigitalVenues, venueId } = this.props

    if (isFilterByDigitalVenues){
      return (
        <React.Fragment>
          <div id="filter-by-digital-offer"
               className={classnames({'is-invisible': !isFilterByDigitalVenues,})}>
            <div className="section">
              <h2 className="main-list-title">
                OFFRE NUMERIQUE
              </h2>
              <div>
                {'Télécharger les réservations pour l\'offre numérique :'}
              </div>
              <select
                onChange={this.onChangeDigitalOffer}
                className="pc-selectbox pl24 py5 fs19"
                id="digitalOffers"
              >
                <option value="" disabled selected>Choisissez une offre dans la liste.</option>
                {offersOptions.map(({ name, id }) => (
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
    if (venueId !== null && !isFilterByDigitalVenues){
      return (
        <React.Fragment>
          <div id="filter-by-offer"
               className={classnames({'is-invisible': isFilterByDigitalVenues,})} >
            <div className="section">
              <h2 className="main-list-title">
                OFFRE
              </h2>
              <div>
                {'Télécharger les réservations pour l\'offre :'}
              </div>
              <select
                onChange={this.onChangeOffer}
                className="pc-selectbox pl24 py5 fs19"
                id="offers"
              >
                <option value="" disabled selected>Choisissez une offre dans la liste.</option>
                {offersOptions.map(({ name, id }) => (
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
