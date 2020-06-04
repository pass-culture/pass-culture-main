import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { Offerer } from './Offerer'
import Main from '../../../layout/Main'
import Titles from '../../../layout/Titles/Titles'
import BankInformation from './BankInformation/BankInformation'
import VenuesContainer from './Venues/VenuesContainer'

class OffererDetails extends PureComponent {
  componentDidMount() {
    const { offererId, loadOffererById } = this.props
    loadOffererById(offererId)
  }

  render() {
    const { offerer, venues } = this.props
    return (
      <Main
        backTo={{ label: 'Vos structures juridiques', path: '/structures' }}
        name="offerer"
      >
        <Titles
          subtitle={offerer.name}
          title="Structure"
        />
        <p className="subtitle op-subtitle">
          {'Détails de la structure rattachée, des lieux et des fournisseurs de ses offres.'}
        </p>
        <div className="section op-content-section">
          <h2 className="main-list-title">
            {'Informations structure'}
          </h2>
          <div className="op-detail">
            <span>
              {'SIREN : '}
            </span>
            <span>
              {offerer.formattedSiren}
            </span>
          </div>
          <div className="op-detail">
            <span>
              {'Désignation : '}
            </span>
            <span>
              {offerer.name}
            </span>
          </div>
          <div className="op-detail">
            <span>
              {'Siège social : '}
            </span>
            <span>
              {`${offerer.address} - ${offerer.postalCode} ${offerer.city}`}
            </span>
          </div>
        </div>
        <BankInformation offerer={offerer} />
        <VenuesContainer
          offererId={offerer.id}
          venues={venues}
        />
      </Main>
    )
  }
}

OffererDetails.propTypes = {
  loadOffererById: PropTypes.func.isRequired,
  offerer: PropTypes.instanceOf(Offerer).isRequired,
  offererId: PropTypes.string.isRequired,
  venues: PropTypes.arrayOf(
    PropTypes.shape({
      address: PropTypes.string,
      city: PropTypes.string,
      id: PropTypes.string,
      managingOffererId: PropTypes.string,
      name: PropTypes.string,
      postalCode: PropTypes.string,
      publicName: PropTypes.string,
    })
  ).isRequired,
}

export default OffererDetails
