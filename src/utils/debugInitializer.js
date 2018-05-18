import get from 'lodash.get'
import { randomHash } from './random'

const LOG_LENGTH = 100

const appendToLog = ({method, values}) => {
  console[method](...values)
  window.logContent = get(window, 'logContent', []).slice(-LOG_LENGTH).concat([{
      method,
      values,
      time: new Date(),
      hash: randomHash(),
    }])
  return values[0]
}

const debug = (...values) => appendToLog({
  method: 'debug',
  values,
})

const log = (...values) => appendToLog({
  method: 'log',
  values,
})


const warn = (...values) => appendToLog({
  method: 'warn',
  values,
})

const error = (...values) => appendToLog({
  method: 'error',
  values,
})


const initialize = () => {
  if (window.logContent) return;
  window.debug = debug;
  window.log = log;
  window.warn = warn;
  window.error = error;
  console.debug('Debug initialized')
  return true;
}


export default initialize();