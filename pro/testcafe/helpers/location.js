import { ClientFunction } from 'testcafe'

export const getPathname = ClientFunction(() => window.location.pathname)

export const getUrlParams = ClientFunction(() => window.location.search)

export const goBack = ClientFunction(() => window.history.back())
