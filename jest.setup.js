// eslint-disable
import { configure } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'
import fetch from 'jest-fetch-mock'

configure({ adapter: new Adapter() })

global.fetch = fetch

process.env.CONTENTFUL_ACCESS_TOKEN = 'ACCESS_TOKEN_ABCDE'
process.env.CONTENTFUL_ENVIRONMENT = 'testing'
process.env.CONTENTFUL_PREVIEW_TOKEN = 'PREVIEW_TOKEN_ABCDE'
process.env.CONTENTFUL_SPACE_ID = '12345'
process.env.BATCH_IS_ENABLED = 'true'
