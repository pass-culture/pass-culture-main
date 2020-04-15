import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { Offerer } from './Offerer'
import Main from '../../../layout/Main'
import Venues from './Venues/Venues'
import Titles from '../../../layout/Titles/Titles'
import RibsUploadFeatureFlip from './FeatureFlip/RibUpload'
import BankInformation from './BankInformation/BankInformation'

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
        <p className="subtitle">
          {'Détails de la structure rattachée, des lieux et des fournisseurs de ses offres.'}
        </p>
        <div>
          <div className="op-detail">
            <label>
              {'SIREN : '}
            </label>
            <span>
              {offerer.siren}
            </span>
          </div>
          <div className="op-detail">
            <label>
              {'Désignation : '}
            </label>
            <span>
              {offerer.name}
            </span>
          </div>
          <div className="op-detail">
            <label>
              {'Siège social : '}
            </label>
            <span>
              {offerer.address}
            </span>
          </div>
          <div className="op-detail">
            <label>
              {'Code postal : '}
            </label>
            <span>
              {offerer.postalCode}
            </span>
          </div>
          <div className="op-detail">
            <label>
              {'Ville : '}
            </label>
            <span>
              {offerer.city}
            </span>
          </div>
        </div>

        <RibsUploadFeatureFlip legacy={<BankInformation.Legacy offerer={offerer} />}>
          <BankInformation offerer={offerer} />
        </RibsUploadFeatureFlip>

        <Venues
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
