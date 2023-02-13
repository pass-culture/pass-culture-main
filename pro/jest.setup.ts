import 'regenerator-runtime/runtime'
import fetchMock from 'jest-fetch-mock'
import '@testing-library/jest-dom'

fetchMock.enableMocks()

fetchMock.mockResponse(req => {
  const msg = `
----------------------------------------------------------------------------
/!\\ UNMOCKED FETCH CALL TO :  ${req.url}
----------------------------------------------------------------------------
` // console.error is fine here
  // eslint-disable-next-line
  console.error(msg)
  return Promise.reject(new Error(msg))
})
