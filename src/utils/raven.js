import Raven from 'raven-js'

import { API_URL, IS_DEV } from './config'
import { version } from '../package.json'

if (!IS_DEV) {
  Raven.config(`${API_URL}/client_errors`, {
    environment: process.env.NODE_ENV,
    logger: 'javascript',
    release: `pro-${version}`,
  }).install()
}
