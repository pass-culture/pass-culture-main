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

  it('should show navigation tabs', () => {
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

  it('should show the INFORMATIONS step if WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS is enabled', () => {
    const offerId = 1
    renderWithProviders(
      <CollectiveOfferEditionNavigation
        activeStep={CollectiveOfferStep.INFORMATION}
        offerId={offerId}
      />,
      { features: ['WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'] }
    )

    const tabs = screen.getAllByRole('listitem')
    expect(tabs).toHaveLength(4)

    const tabDetails = within(tabs[0]).getByRole('link', {
      name: "Détails de l'offre",
    })
    expect(tabDetails).toBeVisible()
    expect(tabDetails.getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/edition`
    )

    const tabDates = within(tabs[1]).getByRole('link', {
      name: 'Dates et prix',
    })
    expect(tabDates).toBeVisible()
    expect(tabDates.getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/stocks/edition`
    )

    const tabInformations = within(tabs[2]).getByRole('link', {
      name: /Informations pratiques/,
    })
    expect(tabs[2]).toHaveAttribute('id', 'selected')
    expect(tabInformations).toBeVisible()
    expect(tabInformations.getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/informations-pratiques/edition`
    )

    const tabEtablissement = within(tabs[3]).getByRole('link', {
      name: 'Établissement et enseignant',
    })
    expect(tabEtablissement).toBeVisible()
    expect(tabEtablissement.getAttribute('href')).toBe(
      `/offre/${offerId}/collectif/etablissement/edition`
    )
  })
})
