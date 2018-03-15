/* global self */
/* eslint no-restricted-globals: ["off", "self"] */

import DexieWrapper from './utils/dexie.wrapper'

let DexieWorker
if (process.env.HAS_WORKERS) {
  const dexieWrapper = new DexieWrapper(self)
  self.addEventListener('message', dexieWrapper.onMessage)
} else {
  DexieWorker = DexieWrapper
}

export default DexieWorker
