import AxeBuilder from '@axe-core/playwright'
import { expect, type Page } from '@playwright/test'

function waitTwoAnimationFrames() {
  return new Promise<void>((resolve) => {
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
  })
}

async function waitForSnackbarIfPresent(page: Page) {
  await page.evaluate(waitTwoAnimationFrames)

  const snackbar = page.locator('[data-testid^="global-snack-bar-"]')

  // Wait for snackbar to be visible (if any)
  try {
    await snackbar.first().waitFor({ state: 'visible', timeout: 500 })
  } catch {
    // If no snackbar, continue
  }
  // Loop: closing one snackbar can be immediately followed by another one.
  while ((await snackbar.count()) > 0) {
    await snackbar.first().waitFor({ state: 'detached' })
  }

  return page.evaluate(() =>
    Promise.allSettled(document.getAnimations().map((a) => a.finished))
  )
}

export async function checkAccessibility(page: Page): Promise<void> {
  const axeBuilder = new AxeBuilder({ page })
  axeBuilder.exclude('iframe[name^="a-"]')

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
