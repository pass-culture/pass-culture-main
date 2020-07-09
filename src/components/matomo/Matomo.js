import PropTypes from 'prop-types'
import { useEffect } from 'react'

import { ANDROID_APPLICATION_ID, MATOMO_GEOLOCATION_GOAL_ID } from '../../utils/config'
import trackPageView from '../../tracking/trackPageView'

const Matomo = ({ history, location, userId, coordinates }) => {
  const Matomo = window._paq

  const { pathname } = location

  Matomo.push(['setCustomUrl', pathname])
  Matomo.push(['setDocumentTitle', document.title])

  if (document.referrer.includes('android-app://' + ANDROID_APPLICATION_ID)) {
    Matomo.push(['setUserId', userId + ' on TWA'])
    Matomo.push(['setCustomVariable', 1, "platform", "application", "visit"])
  } else {
    Matomo.push(['setUserId', userId + ' on WEBAPP'])
    Matomo.push(['setCustomVariable', 1, "platform", "browser", "visit"])
  }


  useEffect(() => {
    const unlisten = history.listen(() => {
      trackPageView()
    })

    return () => {
      unlisten()
    }
  }, [])

  if (location.pathname == '/connexion') {
    Matomo.push(['resetUserId'])
  }

  if (coordinates.latitude && coordinates.longitude) {
    Matomo.push(['trackGoal', MATOMO_GEOLOCATION_GOAL_ID])
  }

  return null
}

Matomo.propTypes = {
  coordinates: PropTypes.shape().isRequired,
  location: PropTypes.shape().isRequired,
  userId: PropTypes.string.isRequired,
}

export default Matomo
