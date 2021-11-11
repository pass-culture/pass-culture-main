import { Offerer } from './Offerer'

export const makeOffererComponentValueObject = (offererSelector, offererId, state) => {
  const offerer = offererSelector(state, offererId)
  return new Offerer(offerer)
}
