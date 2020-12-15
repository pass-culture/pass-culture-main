import PropTypes from 'prop-types'
import React, { Fragment, useCallback, useEffect, useRef } from 'react'
import { Route } from 'react-router-dom'

import { formatToFrenchDecimal } from '../../../../utils/getDisplayPrice'
import CloseLink from '../../../layout/Header/CloseLink/CloseLink'
import BusinessModule from './BusinessModule/BusinessModule'
import { formatPublicName } from './domain/formatPublicName'
import ExclusivityPane from './domain/ValueObjects/ExclusivityPane'
import Offers from './domain/ValueObjects/Offers'
import OffersWithCover from './domain/ValueObjects/OffersWithCover'
import ExclusivityModule from './ExclusivityModule/ExclusivityModule'
import Module from './Module/Module'
import OfferDetailsContainer from './OfferDetails/OfferDetailsContainer'
import Profile from '../Profile/Profile'
import User from '../Profile/ValueObjects/User'
import { setCustomUserId } from '../../../../notifications/setUpBatchSDK'
import BusinessPane from './domain/ValueObjects/BusinessPane'

const MainView = props => {
  const {
    history,
    displayedModules,
    geolocation,
    match,
    user,
    updateCurrentUser,
    algoliaMapping,
  } = props
  const { trackAllModulesSeen, trackAllTilesSeen, trackConsultOffer } = props
  const haveSeenAllModules = useRef(false)
  const modulesListRef = useRef(null)

  useEffect(() => {
    setCustomUserId(user.id)
    updateCurrentUser({ lastConnectionDate: new Date() })
  }, [updateCurrentUser, user.id])

  const checkIfAllModulesHaveBeenSeen = useCallback(() => {
    if (!modulesListRef.current || haveSeenAllModules.current) return
    const navbarHeight = 60
    const modulePaddingBottom = 24
    const hasReachedEndOfPage =
      modulesListRef.current.getBoundingClientRect().bottom +
        navbarHeight -
        modulePaddingBottom -
        document.documentElement.clientHeight <=
      0
    if (hasReachedEndOfPage && modulesListRef.current.children.length > 0) {
      trackAllModulesSeen(displayedModules.length)
      haveSeenAllModules.current = true
    }
  }, [trackAllModulesSeen, displayedModules])

  useEffect(() => {
    // Check on first render if we have seen all modules without scrolling: all modules fit on the page
    checkIfAllModulesHaveBeenSeen()
  }, [checkIfAllModulesHaveBeenSeen])

  const renderModule = (module, row) => {
    if (module instanceof Offers || module instanceof OffersWithCover) {
      return (
        <Module
          geolocation={geolocation}
          historyPush={history.push}
          key={`${row}-module`}
          module={module}
          results={algoliaMapping[module.moduleId]}
          row={row}
          trackAllTilesSeen={trackAllTilesSeen}
          trackConsultOffer={trackConsultOffer}
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

  return (
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
          {displayedModules.map(renderModule)}
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
  algoliaMapping: PropTypes.shape(
    PropTypes.shape({
      hits: PropTypes.arrayOf(PropTypes.shape()).isRequired,
      nbHits: PropTypes.number.isRequired,
      parsedParameters: PropTypes.shape(),
    })
  ).isRequired,
  displayedModules: PropTypes.arrayOf(
    PropTypes.shape(Offers, OffersWithCover, BusinessPane, ExclusivityPane)
  ).isRequired,
  geolocation: PropTypes.shape({
    latitude: PropTypes.number,
    longitude: PropTypes.number,
  }).isRequired,
  history: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
  trackAllModulesSeen: PropTypes.func.isRequired,
  trackAllTilesSeen: PropTypes.func.isRequired,
  trackConsultOffer: PropTypes.func.isRequired,
  updateCurrentUser: PropTypes.func.isRequired,
  user: PropTypes.shape(User).isRequired,
}

export default MainView
