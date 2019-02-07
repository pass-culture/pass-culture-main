import { ClientFunction } from 'testcafe'

export const getPageUrl = ClientFunction(() => window.location.href.toString())
