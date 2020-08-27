import PropTypes from 'prop-types'
import { parse } from 'query-string'
import React, { Component, createRef, Fragment } from 'react'
import { Link, Route } from 'react-router-dom'

import { formatToFrenchDecimal } from '../../../utils/getDisplayPrice'
import { fetchHomepage } from '../../../vendor/contentful/contentful'
import AnyError from '../../layout/ErrorBoundaries/ErrorsPage/AnyError/AnyError'
import CloseLink from '../../layout/Header/CloseLink/CloseLink'
import Icon from '../../layout/Icon/Icon'
import BusinessModule from './BusinessModule/BusinessModule'
import { formatPublicName } from './domain/formatPublicName'
import ExclusivityPane from './domain/ValueObjects/ExclusivityPane'
import Offers from './domain/ValueObjects/Offers'
import OffersWithCover from './domain/ValueObjects/OffersWithCover'
import ExclusivityModule from './ExclusivityModule/ExclusivityModule'
import Module from './Module/Module'
import OfferDetailsContainer from './OfferDetails/OfferDetailsContainer'

class Home extends Component {
  constructor(props) {
    super(props)
    this.state = {
      modules: [],
      fetchingError: false,
      haveSeenAllModules: false,
    }
    this.modulesListRef = createRef()
  }

  componentDidMount() {
    const { history, updateCurrentUser } = this.props
    const queryParams = parse(history.location.search)

    updateCurrentUser({
      lastConnectionDate: new Date(),
    })
    fetchHomepage({ entryId: queryParams['entryId'] })
      .then(modules => {
        this.setState({
          modules: modules,
        })
      })
      .catch(() => {
        this.setState({
          fetchingError: true,
        })
      })
  }

  componentDidUpdate(prevProps, prevState) {
    const { trackAllModulesSeen } = this.props
    const { haveSeenAllModules, modules } = this.state
    if (prevState.modules.length !== modules.length) {
      this.checkIfAllModulesHaveBeenSeen()
    }
    if (prevState.haveSeenAllModules !== haveSeenAllModules) {
      trackAllModulesSeen(modules.length)
    }
  }

  checkIfAllModulesHaveBeenSeen = () => {
    const navbarHeight = 60
    const modulePaddingBottom = 24
    const hasReachedEndOfPage =
      this.modulesListRef.current.getBoundingClientRect().bottom +
        navbarHeight -
        modulePaddingBottom -
        document.documentElement.clientHeight <=
      0
    if (hasReachedEndOfPage) {
      this.setState({ haveSeenAllModules: true })
    }
  }

  renderModule = (module, row) => {
    const { geolocation, history, trackAllTilesSeen } = this.props
    if (module instanceof Offers || module instanceof OffersWithCover) {
      return (
        <Module
          geolocation={geolocation}
          historyPush={history.push}
          key={`${row}-module`}
          module={module}
          row={row}
          trackAllTilesSeen={trackAllTilesSeen}
        />
      )
    } else {
      if (module instanceof ExclusivityPane) {
        return (<ExclusivityModule
          key={`${row}-exclusivity-module`}
          module={module}
                />)
      }
      return (<BusinessModule
        key={`${row}-business-module`}
        module={module}
              />)
    }
  }

  render() {
    const { fetchingError, modules } = this.state
    const { match, user } = this.props
    const { publicName, wallet_balance } = user
    const formattedPublicName = formatPublicName(publicName)
    const formattedWalletBalance = formatToFrenchDecimal(wallet_balance)

    return fetchingError ? (
      <AnyError />
    ) : (
      <Fragment>
        <div
          className="home-wrapper"
          onScroll={this.checkIfAllModulesHaveBeenSeen}
        >
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
          <div
            className="hw-modules"
            ref={this.modulesListRef}
          >
            {modules.map((module, row) => this.renderModule(module, row))}
          </div>
        </div>
        <Route
          exact
          path={`${match.path}/:details(details|transition)/:offerId([A-Z0-9]+)/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
          sensitive
        >
          <div className="home-details-wrapper">
            <CloseLink closeTo="/accueil" />
            <OfferDetailsContainer match={match} />
          </div>
        </Route>
      </Fragment>
    )
  }
}

Home.propTypes = {
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }).isRequired,
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  trackAllModulesSeen: PropTypes.func.isRequired,
  trackAllTilesSeen: PropTypes.func.isRequired,
  updateCurrentUser: PropTypes.func.isRequired,
  user: PropTypes.shape({
    publicName: PropTypes.string,
    wallet_balance: PropTypes.number,
  }).isRequired,
}

export default Home
