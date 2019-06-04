import Raven from 'raven-js'

import { API_URL, APP_VERSION, IS_DEV } from './config'

const { NODE_ENV } = process.env

const initRaven = () => {
  if (IS_DEV) {
    return
  }
  Raven.config(`${API_URL}/client_errors`, {
    environment: NODE_ENV,
    logger: 'javascript',
    release: APP_VERSION,
  }).install()
}

export default initRaven
