import React, { PureComponent } from 'react'
import classnames from "classnames";
import PropTypes from "prop-types";
import {FilterByOffer} from "./FilterByOffer";

export class FilterByDigitalOffer extends PureComponent {

  onChangeDigitalOffer = event => {
    const selectedOffer = document.getElementById("offers")
    const offerId = selectedOffer[selectedOffer.selectedIndex].value
    console.log("OfferId", offerId)
  }

  render() {
    const { offers } = this.props
    const isDigitalChecked = true
    return (
      <React.Fragment>
        <div id="filter-by-digital-offer"
             className={classnames({'is-invisible': !isDigitalChecked,})}>
          <div className="section">
            <h1 className="main-list-title">
              OFFRE NUMERIQUE
            </h1>
          </div>
          <h2>
            {'Sélectionner les réservations pour l\'offre numérique :'}
          </h2>
          <select
            onChange={this.onChangeDigitalOffer}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue="all"
            id="offers"
          >
            {offers.map(({ name, id }) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </select>
        </div>
      </React.Fragment>
    )
  }
}

FilterByOffer.propTypes = {
  offers: PropTypes.array.isRequired,
}
