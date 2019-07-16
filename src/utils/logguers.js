import { IS_DEBUG } from './config'

export const debug = IS_DEBUG ? (...args) => console.debug('DEBUG', ...args) : () => {}
export const log = (...args) => {
  console.log(...args)
  return args && args[0]
}
export const warn = console.warn
