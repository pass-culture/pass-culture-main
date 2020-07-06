import PropTypes from 'prop-types'
import { parse } from 'query-string'
import { useEffect } from 'react'

import { MATOMO_GEOLOCATION_GOAL_ID } from '../../utils/config'
import trackPageView from '../../tracking/trackPageView'

const Matomo = ({ history, location, userId, coordinates }) => {
  const Matomo = window._paq

  const { pathname, search } = location
  const searchParameters = parse(search)
  const searchKeyword = searchParameters['mots-cles']

  Matomo.push(['setCustomUrl', pathname])
  Matomo.push(['setDocumentTitle', document.title])

  useEffect(() => {
    const unlisten = history.listen(() => {
      trackPageView()
    })

    return () => {
      unlisten()
    }
  }, [])

  if (searchKeyword) {
    const categories = searchParameters['categories'] || false
    const numberOfResults = false

    Matomo.push(['trackSiteSearch', searchKeyword, categories, numberOfResults])
  }

  Matomo.push(['setUserId', userId + ' on WEBAPP'])

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
