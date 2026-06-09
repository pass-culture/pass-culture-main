import { screen, within } from '@testing-library/dom'
import { expect } from 'vitest'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferEditionNavigation } from './CollectiveOfferEditionNavigation'
import { CollectiveOfferStep } from './constants'

describe('<CollectiveOfferEditionNavigation />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <CollectiveOfferEditionNavigation
        activeStep={CollectiveOfferStep.DETAILS}
      />
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should not show duplicate button when CAN_DUPLICATE is not allowed', () => {
    renderWithProviders(
      <CollectiveOfferEditionNavigation
        activeStep={CollectiveOfferStep.DETAILS}
        offerId={1}
      />
    )

    const tabs = screen.getAllByRole('listitem')
    expect(tabs).toHaveLength(3)
    expect(tabs[0]).toHaveAttribute('id', 'selected')
    expect(
      within(tabs[0]).getByRole('link', { name: /Détails de l'offre/ })
    ).toBeVisible()
    expect(
      within(tabs[1]).getByRole('link', { name: 'Dates et prix' })
    ).toBeVisible()
    expect(
      within(tabs[2]).getByRole('link', {
        name: 'Établissement et enseignant',
      })
    ).toBeVisible()
  })
})
