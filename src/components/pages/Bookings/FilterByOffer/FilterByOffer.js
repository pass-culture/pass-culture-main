import React, { Fragment, PureComponent } from 'react'
import PropTypes from 'prop-types'

import FilterByDateContainer from '../FilterByDate/FilterByDateContainer'

export class FilterByOffer extends PureComponent {
  componentDidMount() {
    const { loadOffers } = this.props
    loadOffers()
  }

  render() {
    const {
      isFilterByDigitalVenues,
      offerId,
      offersOptions,
      selectBookingsForOffers,
      showDateSection,
    } = this.props

    return (
      <Fragment>
        <div className="section">
          <h2 className="main-list-title">
            {isFilterByDigitalVenues ? 'Offre numérique' : 'Offre'}
          </h2>
        </div>
        <div id="filter-by-offer">
          <label htmlFor="offers">
            {"Télécharger les réservations pour l'offre "}
            {isFilterByDigitalVenues ? 'numérique' : ''}
            {':'}
          </label>
          <select
            className="pc-selectbox pl24 py5 fs19"
            id="offers"
            onBlur={selectBookingsForOffers}
            onChange={selectBookingsForOffers}
            value={offerId}
          >
            <option
              disabled
              label=" "
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
}

FilterByOffer.propTypes = {
  isFilterByDigitalVenues: PropTypes.bool.isRequired,
  loadOffers: PropTypes.func.isRequired,
  offerId: PropTypes.string,
  offersOptions: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  selectBookingsForOffers: PropTypes.func.isRequired,
  showDateSection: PropTypes.bool.isRequired,
}
