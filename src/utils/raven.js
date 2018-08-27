import Raven from 'raven-js'

import { API_URL } from './config'
import { version } from '../../package.json'

if (process.env.NODE_ENV !== 'development') {
  Raven.config(`${API_URL}/client_errors`, {
    environment: process.env.NODE_ENV,
    logger: 'javascript',
    release: `pro-${version}`,
  }).install()
}
