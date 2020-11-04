import PropTypes from 'prop-types'
import React, { Fragment, useEffect, useRef, useState } from 'react'
import MainView from './MainView/MainView'
import User from './Profile/ValueObjects/User'
import { getCurrentPosition } from '../../../utils/geolocation'
import LoaderContainer from '../../layout/Loader/LoaderContainer'

const Home = ({
  geolocation,
  history,
  match,
  trackAllModulesSeen,
  trackAllTilesSeen,
  updateCurrentUser,
  user,
}) => {
  const [isLoading, setIsLoading] = useState(true)
  const geolocationRef = useRef(geolocation)

  useEffect(() => {
    const waitForCoordinates = async () => {
      try {
        const confirmedGeolocation = await getCurrentPosition(geolocation)
        geolocationRef.current = confirmedGeolocation
        setIsLoading(false)
      } catch (error) {
        setIsLoading(false)
      }
    }
    waitForCoordinates()
  }, [geolocation])

  return (
    <Fragment>
      {isLoading && <LoaderContainer />}
      {!isLoading && (
        <MainView
          geolocation={geolocationRef.current}
          history={history}
          match={match}
          trackAllModulesSeen={trackAllModulesSeen}
          trackAllTilesSeen={trackAllTilesSeen}
          updateCurrentUser={updateCurrentUser}
          user={user}
        />
      )}
    </Fragment>
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
  updateCurrentUser: PropTypes.func.isRequired,
  user: PropTypes.instanceOf(User).isRequired,
}

export default Home
