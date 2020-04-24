import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'
import withLogin from './withLogin'

import withFrenchQueryRouter from '../withFrenchQueryRouter'
import { getRedirectionPath } from './helpers'

export const handleFail = (state, action, ownProps) => {
  const { history, location } = ownProps
  const { pathname, search } = location

  const fromUrl = encodeURIComponent(`${pathname}${search}`)

  history.push(`/connexion?de=${fromUrl}`)
}

export const handleSuccess = (state, action, ownProps) => {
  const {
    payload: { datum },
  } = action
  const currentUser = datum
  const { history, location } = ownProps

  const redirect = getRedirectionPath({
    currentUser,
    ...location,
  })

  if (redirect) {
    history.push(redirect)
  }
}

const withRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleFail,
    handleSuccess,
    isRequired: true,
    requestData,
  })
)

export default withRequiredLogin
