import { configure } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetch from 'jest-fetch-mock'
import 'babel-polyfill'

configure({ adapter: new Adapter() })

global.fetch = fetch
jest.spyOn(global, 'scrollTo').mockImplementation()

fetch.mockResponse(req => {
  const msg = `
  ----------------------------------------------------------------------------
   /!\\ UNMOCKED FETCH CALL TO :  ${req.url}
  ----------------------------------------------------------------------------
  `
  console.error(msg)
  return Promise.reject(new Error(msg))
})

jest.mock('tracking/mediaCampaignsTracking')
