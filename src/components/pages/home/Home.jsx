import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { Link, Route } from 'react-router-dom'

import { formatToFrenchDecimal } from '../../../utils/getDisplayPrice'
import { fetchHomepage } from '../../../vendor/contentful/contentful'
import HeaderContainer from '../../layout/Header/HeaderContainer'
import Icon from '../../layout/Icon/Icon'
import BusinessModule from './BusinessModule/BusinessModule'
import { formatPublicName } from './domain/formatPublicName'
import Offers from './domain/ValueObjects/Offers'
import OffersWithCover from './domain/ValueObjects/OffersWithCover'
import Module from './Module/Module'
import OfferDetailsContainer from './OfferDetails/OfferDetailsContainer'
import ExclusivityPane from './domain/ValueObjects/ExclusivityPane'
import ExclusivityModule from './ExclusivityModule/ExclusivityModule'
import { parse } from 'query-string'

class Home extends Component {
  constructor(props) {
    super(props)
    this.state = {
      modules: [],
    }
  }

  componentDidMount() {
    const { history } = this.props
    const queryParams = parse(history.location.search)

    fetchHomepage({ entryId: queryParams['entryId'] }).then(modules =>
      this.setState({
        modules: modules,
      }))
  }

  renderModule = (module, row) => {
    const { history } = this.props
    if (module instanceof Offers || module instanceof OffersWithCover) {
      return (
        <Module
          historyPush={history.push}
          key={`${row}-module`}
          module={module}
          row={row}
        />
      )
    } else {
      if (module instanceof ExclusivityPane) {
        return (
          <ExclusivityModule
            key={`${row}-exclusivity-module`}
            module={module}
          />
        )
      }
      return (
        <BusinessModule
          key={`${row}-business-module`}
          module={module}
        />
      )
    }
  }

  render() {
    const { modules } = this.state
    const { match, user } = this.props
    const { publicName, wallet_balance } = user
    const formattedPublicName = formatPublicName(publicName)
    const formattedWalletBalance = formatToFrenchDecimal(wallet_balance)
    const atLeastOneModule = modules.length > 0

    return (
      <Fragment>
        <div className="home-wrapper">
          <section className="hw-header">
            <div className="hw-account">
              <Link to="/profil">
                <Icon
                  className="hw-account-image"
                  svg="ico-informations-white"
                />
              </Link>
            </div>
            <div className="hw-pseudo">
              {`Bonjour ${formattedPublicName}`}
            </div>
            <div className="hw-wallet">
              {`Tu as ${formattedWalletBalance} € sur ton pass`}
            </div>
          </section>
          {atLeastOneModule && (
            <div className="hw-modules">
              {modules.map((module, row) => this.renderModule(module, row))}
            </div>
          )}
        </div>
        <Route
          exact
          path={`${match.path}/:details(details|transition)/:offerId([A-Z0-9]+)/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
          sensitive
        >
          <div className="offer-details">
            <HeaderContainer
              backTo="/accueil"
              title="Offre"
            />
            <OfferDetailsContainer match={match} />
          </div>
        </Route>
      </Fragment>
    )
  }
}

Home.propTypes = {
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  user: PropTypes.shape({
    publicName: PropTypes.string,
    wallet_balance: PropTypes.number,
  }).isRequired,
}

export default Home
