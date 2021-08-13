import { configure } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetch from 'jest-fetch-mock'
import 'babel-polyfill'

configure({ adapter: new Adapter() })

global.fetch = fetch
jest.spyOn(global, 'scrollTo').mockImplementation()

fetch.mockResponse(req => {
  console.error(`
----------------------------------------------------------------------------
 /!\\ UNMOCKED FETCH CALL TO :  ${req.url}
----------------------------------------------------------------------------
`)
  return Promise.reject(new Error('UNMOCKED FETCH CALL'))
})

jest.mock('tracking/mediaCampaignsTracking')
