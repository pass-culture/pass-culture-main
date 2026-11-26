import { screen } from '@testing-library/dom'
import { expect } from 'vitest'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferEditionNavigation } from './CollectiveOfferEditionNavigation'
import { CollectiveOfferStep } from './constants'

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

describe('<CollectiveOfferEditionNavigation />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(
      <div>
        <CollectiveOfferEditionNavigation
          activeStep={CollectiveOfferStep.DETAILS}
        />
        <div id="panel-DETAILS" role="tabpanel"></div>
        <div id="panel-STOCKS" role="tabpanel"></div>
        <div id="panel-INFORMATION" role="tabpanel"></div>
        <div id="panel-INSTITUTION" role="tabpanel"></div>
      </div>
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should show navigation tabs', () => {
    renderWithProviders(
      <div>
        <CollectiveOfferEditionNavigation
          activeStep={CollectiveOfferStep.DETAILS}
          offerId={1}
        />
        <div id="panel-DETAILS" role="tabpanel"></div>
        <div id="panel-STOCKS" role="tabpanel"></div>
        <div id="panel-INFORMATION" role="tabpanel"></div>
        <div id="panel-INSTITUTION" role="tabpanel"></div>
      </div>
    )

    expect(
      screen.getByRole('tab', { name: /Détails de l'offre/ })
    ).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Dates et prix' })).toBeVisible()
    expect(
      screen.getByRole('tab', {
        name: 'Informations pratiques',
      })
    ).toBeVisible()
    expect(
      screen.getByRole('tab', {
        name: 'Établissement et enseignant',
      })
    ).toBeVisible()
  })

  it('should show the INFORMATIONS step', () => {
    const offerId = 1
    renderWithProviders(
      <div>
        <CollectiveOfferEditionNavigation
          activeStep={CollectiveOfferStep.INFORMATION}
          offerId={offerId}
        />
        <div id="panel-DETAILS" role="tabpanel"></div>
        <div id="panel-STOCKS" role="tabpanel"></div>
        <div id="panel-INFORMATION" role="tabpanel"></div>
        <div id="panel-INSTITUTION" role="tabpanel"></div>
      </div>
    )

    const tabDetails = screen.getByRole('tab', {
      name: "Détails de l'offre",
    })
    expect(tabDetails).toBeVisible()
    expect(tabDetails).toHaveAttribute('aria-selected', 'false')

    const tabDates = screen.getByRole('tab', {
      name: 'Dates et prix',
    })
    expect(tabDates).toBeVisible()

    const tabInformations = screen.getByRole('tab', {
      name: /Informations pratiques/,
    })
    expect(tabInformations).toBeVisible()
    expect(tabInformations).toHaveAttribute('aria-selected', 'true')

    const tabEtablissement = screen.getByRole('tab', {
      name: 'Établissement et enseignant',
    })
    expect(tabEtablissement).toBeVisible()
  })
})
