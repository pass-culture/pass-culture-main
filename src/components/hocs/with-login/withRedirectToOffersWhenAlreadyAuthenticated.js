import { compose } from 'redux'
import withLogin from 'with-react-redux-login'

import withFrenchQueryRouter from '../withFrenchQueryRouter'

export const withRedirectToOffersWhenAlreadyAuthenticated = compose(
  withFrenchQueryRouter,
  withLogin({
    handleSuccess: (state, action, ownProps) => {
      const { currentUser, history } = ownProps
      const { hasOffers, hasPhysicalVenues } = currentUser || false
      const hasOffersWithPhysicalVenues = hasOffers && hasPhysicalVenues
      const redirectUrl = (hasOffersWithPhysicalVenues || hasPhysicalVenues)
        ? '/offres'
        : '/structures'
      history.push(redirectUrl)
    },
    isRequired: false
  })
)

export default withRedirectToOffersWhenAlreadyAuthenticated
