import PropTypes from 'prop-types'
import React from 'react'
import MainView from './MainView/MainView'
import User from './Profile/ValueObjects/User'

const Home = ({
  geolocation,
  history,
  match,
  trackAllModulesSeen,
  trackAllTilesSeen,
  updateCurrentUser,
  user,
}) => (
  <MainView
    geolocation={geolocation}
    history={history}
    match={match}
    trackAllModulesSeen={trackAllModulesSeen}
    trackAllTilesSeen={trackAllTilesSeen}
    updateCurrentUser={updateCurrentUser}
    user={user}
  />
)

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
