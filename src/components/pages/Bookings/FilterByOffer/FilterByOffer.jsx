import React, { Fragment, PureComponent } from 'react'
import PropTypes from 'prop-types'

import FilterByDateContainer from '../FilterByDate/FilterByDateContainer'

class FilterByOffer extends PureComponent {
  componentDidMount() {
    const { loadOffers, venueId } = this.props
    loadOffers(venueId)
  }

  componentDidUpdate(prevProps) {
    const { loadOffers, venueId } = this.props

    if (prevProps.venueId !== venueId) {
      loadOffers(venueId)
    }
  }

  render() {
    const {
      isFilteredByDigitalVenues,
      offerId,
      offersOptions,
      showDateSection,
      updateOfferId,
    } = this.props

    return (
      <Fragment>
        <div className="section">
          <h2 className="main-list-title">
            {isFilteredByDigitalVenues ? 'Offre numérique' : 'Offre'}
          </h2>
        </div>
        <div id="filter-by-offer">
          <label htmlFor="offers">
            {"Télécharger les réservations pour l'offre "}
            {isFilteredByDigitalVenues ? 'numérique ' : ''}
            {':'}
          </label>
          <select
            className="pc-selectbox"
            id="offers"
            onBlur={updateOfferId}
            onChange={updateOfferId}
            value={offerId}
          >
            <option
              disabled
              label=" - Choisissez une offre dans la liste - "
              selected
            />
            {offersOptions.map(({ name, id }) => (
              <option
                key={id}
                value={id}
              >
                {name}
              </option>
            ))}
          </select>
        </div>
        {showDateSection && <FilterByDateContainer />}
      </Fragment>
    )
  }
}

FilterByOffer.defaultProps = {
  offerId: '',
  venueId: 'all',
}

FilterByOffer.propTypes = {
  isFilteredByDigitalVenues: PropTypes.bool.isRequired,
  loadOffers: PropTypes.func.isRequired,
  offerId: PropTypes.string,
  offersOptions: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  showDateSection: PropTypes.bool.isRequired,
  updateOfferId: PropTypes.func.isRequired,
  venueId: PropTypes.string,
}

export default FilterByOffer
