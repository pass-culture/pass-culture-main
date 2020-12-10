import PropTypes from 'prop-types'
import { parse } from 'query-string'
import React, { Fragment, useCallback, useEffect, useRef, useState } from 'react'
import { Link, Route } from 'react-router-dom'

import { formatToFrenchDecimal } from '../../../../utils/getDisplayPrice'
import { fetchHomepage } from '../../../../vendor/contentful/contentful'
import AnyError from '../../../layout/ErrorBoundaries/ErrorsPage/AnyError/AnyError'
import CloseLink from '../../../layout/Header/CloseLink/CloseLink'
import BusinessModule from './BusinessModule/BusinessModule'
import { formatPublicName } from './domain/formatPublicName'
import ExclusivityPane from './domain/ValueObjects/ExclusivityPane'
import Offers from './domain/ValueObjects/Offers'
import OffersWithCover from './domain/ValueObjects/OffersWithCover'
import ExclusivityModule from './ExclusivityModule/ExclusivityModule'
import Module from './Module/Module'
import OfferDetailsContainer from './OfferDetails/OfferDetailsContainer'
import Icon from '../../../layout/Icon/Icon'
import Profile from '../Profile/Profile'
import User from '../Profile/ValueObjects/User'
import { setCustomUserId } from '../../../../notifications/setUpBatchSDK'

const MainView = props => {
  const { history, geolocation, match, user, updateCurrentUser } = props
  const { trackAllModulesSeen, trackAllTilesSeen } = props
  const [modules, setModules] = useState([])
  const [fetchingError, setFetchingError] = useState(false)
  const [haveSeenAllModules, setHaveSeenAllModules] = useState(false)

  const modulesListRef = useRef(null)

  useEffect(() => {
    setCustomUserId(user.id)
    updateCurrentUser({ lastConnectionDate: new Date() })
  }, [updateCurrentUser, user.id])

  useEffect(() => {
    const { entryId } = parse(history.location.search)
    fetchHomepage({ entryId })
      .then(setModules)
      .catch(() => setFetchingError(true))
  }, [history.location.search])

  useEffect(() => {
    if (haveSeenAllModules) {
      trackAllModulesSeen(modules.length)
    }
  }, [haveSeenAllModules, trackAllModulesSeen, modules.length])

  const checkIfAllModulesHaveBeenSeen = useCallback(() => {
    const navbarHeight = 60
    const modulePaddingBottom = 24
    const hasReachedEndOfPage =
      modulesListRef.current.getBoundingClientRect().bottom +
        navbarHeight -
        modulePaddingBottom -
        document.documentElement.clientHeight <=
      0
    if (hasReachedEndOfPage) {
      setHaveSeenAllModules(true)
    }
  }, [])

  const renderModule = (module, row) => {
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

  return fetchingError ? (
    <AnyError />
  ) : (
    <Fragment>
      <Route path={`${match.path}/profil`}>
        <Profile
          history={history}
          match={match}
          user={user}
        />
      </Route>
      <div
        className="home-wrapper"
        onScroll={checkIfAllModulesHaveBeenSeen}
      >
        <section className="hw-header">
          <div className="hw-account">
            <Link to="/accueil/profil">
              <Icon
                className="hw-account-image"
                svg="ico-informations-white"
              />
            </Link>
          </div>
          <div className="hw-pseudo">
            {`Bonjour ${formatPublicName(user.publicName)}`}
          </div>
          <div className="hw-wallet">
            {`Tu as ${formatToFrenchDecimal(user.wallet_balance)} € sur ton pass`}
          </div>
        </section>
        <div
          className="hw-modules"
          ref={modulesListRef}
        >
          {modules.map(renderModule)}
        </div>
      </div>
      <Route
        exact
        path={`${match.path}/:details(details|transition)/:offerId([A-Z0-9]+)/:booking(reservation)?/:bookingId([A-Z0-9]+)?/:cancellation(annulation)?/:confirmation(confirmation)?`}
        sensitive
      >
        <div className="home-details-wrapper">
          <CloseLink closeTo="/accueil" />
          <OfferDetailsContainer
            match={match}
            withHeader={false}
          />
        </div>
      </Route>
    </Fragment>
  )
}

MainView.propTypes = {
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }).isRequired,
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  trackAllModulesSeen: PropTypes.func.isRequired,
  trackAllTilesSeen: PropTypes.func.isRequired,
  updateCurrentUser: PropTypes.func.isRequired,
  user: PropTypes.shape(User).isRequired,
}

export default MainView
