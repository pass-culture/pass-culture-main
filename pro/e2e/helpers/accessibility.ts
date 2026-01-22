import AxeBuilder from '@axe-core/playwright'
import { expect, type Page } from '@playwright/test'

export async function checkAccessibility(page: Page): Promise<void> {
  const axeBuilder = new AxeBuilder({ page })
  axeBuilder.exclude('iframe[name^="a-"]')
  const results = await axeBuilder.analyze()
  expect(results.violations).toHaveLength(0)
}
