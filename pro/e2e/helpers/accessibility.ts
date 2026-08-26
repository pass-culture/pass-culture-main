import AxeBuilder from '@axe-core/playwright'
import { expect, type Page } from '@playwright/test'

async function waitForSnackbarIfPresent(page: Page) {
  const snackbar = page.locator('[data-testid^="global-snack-bar-"]')

  // If there is a snackbar, wait for it to be detached
  if ((await snackbar.count()) > 0) {
    await snackbar.waitFor({ state: 'detached' })
  }
  return page.evaluate(() =>
    Promise.allSettled(document.getAnimations().map((a) => a.finished))
  )
}

export async function checkAccessibility(
  page: Page,
  disabledRules: string[] = []
): Promise<void> {
  const axeBuilder = new AxeBuilder({ page })
  axeBuilder.exclude('iframe[name^="a-"]')

  if (disabledRules.length > 0) {
    axeBuilder.disableRules(disabledRules)
  }

  await waitForSnackbarIfPresent(page)

  const results = await axeBuilder.analyze()

  if (results.violations.length > 0) {
    results.violations.forEach((violation) => {
      // biome-ignore lint/suspicious/noConsole: log for tests
      console.log({
        id: violation.id,
        impact: violation.impact ?? 'unknown',
        description: violation.description,
        nodes: violation.nodes.map((node) => ({
          html: node.html,
          target: node.target as string[],
        })),
      })
    })
  }

  expect(results.violations).toHaveLength(0)

  return Promise.resolve()
}
