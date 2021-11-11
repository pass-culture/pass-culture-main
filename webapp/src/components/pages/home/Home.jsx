import PropTypes from 'prop-types'
import React, { useEffect, useRef } from 'react'

import MainView from './MainView/MainView'
import useDisplayedHomemodules from './MainView/useDisplayedHomemodules'
import { getCurrentPosition } from '../../../utils/geolocation'
import LoaderContainer from '../../layout/Loader/LoaderContainer'
import { campaignTracker } from '../../../tracking/mediaCampaignsTracking'
import AnyError from '../../layout/ErrorBoundaries/ErrorsPage/AnyError/AnyError'
import User from '../profile/ValueObjects/User'
import { dehumanizeId } from '../../../utils/dehumanizeId/dehumanizeId'

const Home = ({
  geolocation,
  history,
  match,
  trackAllModulesSeen,
  trackAllTilesSeen,
  trackConsultOffer,
  trackGeolocation,
  trackRecommendationModuleSeen,
  trackSeeMoreHasBeenClicked,
  updateCurrentUser,
  useAppSearch,
  user,
}) => {
  const geolocationRef = useRef(geolocation)
  const {
    displayedModules,
    isError,
    isLoading,
    algoliaMapping,
    recommendedHits,
  } = useDisplayedHomemodules(history, geolocationRef.current, dehumanizeId(user.id), useAppSearch)

  useEffect(() => {
    campaignTracker.home()
  }, [])

  useEffect(() => {
    const isGeolocated = geolocation && geolocation.latitude && geolocation.longitude
    if (isGeolocated) {
      trackGeolocation()
    }
  }, [geolocation, trackGeolocation])

  useEffect(() => {
    const waitForCoordinates = async () => {
      try {
        const confirmedGeolocation = await getCurrentPosition(geolocation)
        geolocationRef.current = confirmedGeolocation
      } catch (error) {
        return
      }
    }
    waitForCoordinates()
  }, [geolocation])

  if (isError) return <AnyError />
  if (isLoading) return <LoaderContainer />

  return (
    <MainView
      algoliaMapping={algoliaMapping}
      displayedModules={displayedModules}
      geolocation={geolocationRef.current}
      history={history}
      match={match}
      recommendedHits={recommendedHits}
      trackAllModulesSeen={trackAllModulesSeen}
      trackAllTilesSeen={trackAllTilesSeen}
      trackConsultOffer={trackConsultOffer}
      trackRecommendationModuleSeen={trackRecommendationModuleSeen}
      trackSeeMoreHasBeenClicked={trackSeeMoreHasBeenClicked}
      updateCurrentUser={updateCurrentUser}
      user={user}
    />
  )
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
  trackConsultOffer: PropTypes.func.isRequired,
  trackGeolocation: PropTypes.func.isRequired,
  trackRecommendationModuleSeen: PropTypes.func.isRequired,
  trackSeeMoreHasBeenClicked: PropTypes.func.isRequired,
  updateCurrentUser: PropTypes.func.isRequired,
  useAppSearch: PropTypes.bool.isRequired,
  user: PropTypes.shape(User).isRequired,
}

export default Home
