// eslint-disable
import { configure } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetch from 'jest-fetch-mock'

configure({ adapter: new Adapter() })

global.fetch = fetch
