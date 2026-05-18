import type { Page } from '@playwright/test'

export function mockSiretCheck(page: Page) {
  return page.route('/structure/check/*', (route) => {
    return route.fulfill({
      status: 204,
      contentType: 'application/json',
    })
  })
}
