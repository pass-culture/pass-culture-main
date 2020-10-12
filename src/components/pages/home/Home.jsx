import PropTypes from 'prop-types'
import React, { Fragment, useState } from 'react'
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
  const userCoordinates = getCurrentPosition(geolocation).then(userCoordinates => {
    setIsLoading(false)
    return userCoordinates
  })
  return (
    <Fragment>
      {isLoading && <LoaderContainer />}
      {!isLoading && (
        <MainView
          geolocation={userCoordinates}
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
