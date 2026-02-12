import AxeBuilder from '@axe-core/playwright'
import { expect, type Page } from '@playwright/test'

async function runAxe(page: Page) {
  const axeBuilder = new AxeBuilder({ page })
  axeBuilder.exclude('iframe[name^="a-"]')
  const results = await axeBuilder.analyze()
  return results
}

export async function checkAccessibility(page: Page): Promise<void> {
  const results = await runAxe(page)
  expect(results.violations).toHaveLength(0)
}

export async function logAccessibilityViolations(page: Page): Promise<void> {
  const results = await runAxe(page)
  if (results.violations.length > 0) {
    console.warn(
      `[a11y] ${results.violations.length} violation(s) axe :`,
      JSON.stringify(results.violations, null, 2)
    )
  }
}
