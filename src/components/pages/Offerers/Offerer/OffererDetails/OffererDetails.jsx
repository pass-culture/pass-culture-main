import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { NavLink } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'

import ApiKey from './ApiKey/ApiKeyContainer'
import BankInformation from './BankInformation/BankInformation'
import { Offerer } from './Offerer'
import VenuesContainer from './Venues/VenuesContainer'

class OffererDetails extends PureComponent {
  componentDidMount() {
    const { offererId, loadOffererById } = this.props
    loadOffererById(offererId)
  }

  render() {
    const { offerer, venues } = this.props
    return (
      <div className="offerer-page">
        <NavLink
          className="back-button has-text-primary"
          to={`/accueil?structure=${offerer.id}`}
        >
          <Icon svg="ico-back" />
          {'Accueil'}
        </NavLink>
        <PageTitle title="Détails de votre structure" />
        <Titles
          subtitle={offerer.name}
          title="Structure"
        />
        <p className="op-teaser">
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
        {offerer.areBankInformationProvided && <BankInformation offerer={offerer} />}
        <ApiKey
          maxAllowedApiKeys={offerer.apiKey.maxAllowed}
          offererId={offerer.id}
          savedApiKeys={offerer.apiKey.savedApiKeys}
        />
        <VenuesContainer
          offererId={offerer.id}
          venues={venues}
        />
      </div>
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
