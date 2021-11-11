import { MATOMO_GEOLOCATION_GOAL_ID } from '../utils/config'

export default () => {
  window._paq.push(['trackGoal', MATOMO_GEOLOCATION_GOAL_ID])
}
