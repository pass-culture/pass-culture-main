import DexieWrapper from './utils/dexie.wrapper'

const dexieWrapper = new DexieWrapper(self)

self.addEventListener('message', dexieWrapper.onMessage)
