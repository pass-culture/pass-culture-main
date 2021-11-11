import { ClientFunction } from 'testcafe'

const getPageUrl = ClientFunction(() => window.location.href.toString())

export default getPageUrl
