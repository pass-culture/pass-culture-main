import PropTypes from 'prop-types'
import React from 'react'
import { Route, Switch } from 'react-router'
import MainView from './MainView/MainView'
import Profile from './Profile/Profile'
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
  <Switch>
    <Route path={`${match.path}/profil`}>
      <Profile
        history={history}
        match={match}
        user={user}
      />
    </Route>
    <Route path={match.path}>
      <MainView
        geolocation={geolocation}
        history={history}
        match={match}
        trackAllModulesSeen={trackAllModulesSeen}
        trackAllTilesSeen={trackAllTilesSeen}
        updateCurrentUser={updateCurrentUser}
        user={user}
      />
    </Route>
  </Switch>
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
