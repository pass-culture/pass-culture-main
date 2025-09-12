import fetchPolyfill, { Request as RequestPolyfill } from 'node-fetch'

// https://github.com/reduxjs/redux-toolkit/issues/4966#issuecomment-3115230061
Object.defineProperty(global, 'fetch', {
  // MSW will overwrite this to intercept requests
  writable: true,
  value: fetchPolyfill,
})
Object.defineProperty(global, 'Request', {
  writable: false,
  value: RequestPolyfill,
})
