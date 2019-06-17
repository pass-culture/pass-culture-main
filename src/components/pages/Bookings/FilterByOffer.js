import React, { PureComponent } from 'react'
import classnames from 'classnames'
import PropTypes from 'prop-types'

export class FilterByOffer extends PureComponent {

  onChangeOffer = event => {
    const selectedOffer = document.getElementById("offers")
    const offerId = selectedOffer[selectedOffer.selectedIndex].value
    console.log("OfferId", offerId)
  }

  onChangeDigitalOffer = event => {
    const selectedDigitalOffer = document.getElementById("offers")
    const digitalOfferId = selectedDigitalOffer[selectedDigitalOffer.selectedIndex].value
    console.log("OfferId", digitalOfferId)
  }


  render() {
    const { offers } = this.props
    const isDigitalChecked = true

    if (!isDigitalChecked){
      return (
        <React.Fragment>
          <div id="filter-by-offer"
               className={classnames({'is-invisible': isDigitalChecked,})} >
            <div className="section">
              <h1 className="main-list-title">
                OFFRE
              </h1>
            </div>
            <h2>
              {'Sélectionner les réservations pour l\'offre :'}
            </h2>
            <select
              onChange={this.onChangeOffer}
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

