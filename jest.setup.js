import { configure } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetch from 'jest-fetch-mock'
import 'babel-polyfill'

configure({ adapter: new Adapter() })

global.fetch = fetch
jest.spyOn(global, 'scrollTo').mockImplementation()

jest.mock('tracking/mediaCampaignsTracking')
