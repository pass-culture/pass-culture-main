import React, { Fragment, PureComponent } from 'react'
import PropTypes from 'prop-types'

import { FilterByVenue } from './FilterByVenue'
import FilterByDateContainer from './FilterByDateContainer'

export class FilterByOffer extends PureComponent {
  componentDidMount() {
    this.props.loadOffers()
  }

  onChangeOffer = event => {
    this.props.selectBookingsForOffers(event.target.value)
  }

  render() {
    const { offersOptions, isFilterByDigitalVenues, venueId } = this.props

    const all = isFilterByDigitalVenues ? 'allDigital' : 'allNonDigital'

    if (
      (venueId !== '' && !isFilterByDigitalVenues) ||
      isFilterByDigitalVenues
    ) {
      return (
        <Fragment>
          <div className="section">
            <h2 className="main-list-title">
              {isFilterByDigitalVenues ? 'Offre numérique' : 'Offre'}
            </h2>
          </div>
          <div id="filter-by-offer">
            <label htmlFor="offers">
              Télécharger les réservations pour l'offre{' '}
              {isFilterByDigitalVenues ? 'numérique' : ''} :
            </label>
            <select
              id="offers"
              className="pc-selectbox pl24 py5 fs19"
              onChange={this.onChangeOffer}
              defaultValue="">
              <option value="">Choisissez une offre dans la liste.</option>
              <option value={all}>Toutes les offres</option>
              {offersOptions.map(({ name, id }) => (
                <option key={id} value={id}>
                  {name}
                </option>
              ))}
            </select>
          </div>
          <FilterByDateContainer />
        </Fragment>
      )
    }

    return null
  }
}

FilterByVenue.defaultProps = {
  offerId: '',
  venueId: '',
}

FilterByOffer.propTypes = {
  offersOptions: PropTypes.array.isRequired,
  isFilterByDigitalVenues: PropTypes.bool.isRequired,
  loadOffers: PropTypes.func.isRequired,
  offerId: PropTypes.string,
  venueId: PropTypes.string,
}
