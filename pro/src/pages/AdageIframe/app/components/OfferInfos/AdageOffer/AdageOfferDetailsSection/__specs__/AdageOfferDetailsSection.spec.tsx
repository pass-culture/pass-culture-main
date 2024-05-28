import { screen } from '@testing-library/react'

import { EacFormat } from 'apiClient/adage'
import { defaultCollectiveTemplateOffer } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  AdageOfferDetailsSection,
  AdageOfferDetailsSectionProps,
} from '../AdageOfferDetailsSection'

function renderAdageOfferDetailsSection(
  props: AdageOfferDetailsSectionProps = {
    offer: defaultCollectiveTemplateOffer,
  }
) {
  return renderWithProviders(<AdageOfferDetailsSection {...props} />)
}

describe('AdageOfferDetailsSection', () => {
  it('should display the list of domains of the offer', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        domains: [
          {
            id: 1,
            name: 'test domain 1',
          },
          {
            id: 2,
            name: 'test domain 2',
          },
        ],
      },
    })

    expect(
      screen.getByRole('heading', { name: 'Domaines artistiques' })
    ).toBeInTheDocument()
    expect(screen.getByText('test domain 1')).toBeInTheDocument()
    expect(screen.getByText('test domain 2')).toBeInTheDocument()
  })

  it('should not display the domains section if the offer has no domains', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        domains: [],
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Domaines artistiques' })
    ).not.toBeInTheDocument()
  })

  it('should display the list of formats of the offer', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        formats: [EacFormat.CONCERT, EacFormat.VISITE_GUID_E],
      },
    })

    expect(
      screen.getByRole('heading', { name: 'Format de l’offre' })
    ).toBeInTheDocument()
    expect(screen.getByText('Concert')).toBeInTheDocument()
    expect(screen.getByText('Visite guidée')).toBeInTheDocument()
  })

  it('should not display the formats section if the offer has no formats', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        formats: [],
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Format de l’offre' })
    ).not.toBeInTheDocument()
  })

  it('should display the national program of the offer', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        nationalProgram: { name: 'National program test', id: 1 },
      },
    })

    expect(
      screen.getByRole('heading', { name: 'Dispositif national' })
    ).toBeInTheDocument()
    expect(screen.getByText('National program test')).toBeInTheDocument()
  })

  it('should not display the national program section if the offer has no national program', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        nationalProgram: undefined,
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Dispositif national' })
    ).not.toBeInTheDocument()
  })

  it('should display the offer duration', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        durationMinutes: 120,
      },
    })

    expect(screen.getByRole('heading', { name: 'Durée' })).toBeInTheDocument()
    expect(screen.getByText('2h')).toBeInTheDocument()
  })

  it('should not display duration section if the offer has no duration', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        durationMinutes: undefined,
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Durée' })
    ).not.toBeInTheDocument()
  })

  it('should display the offer description', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        description: 'A great description for a great offer',
      },
    })

    expect(
      screen.getByRole('heading', { name: 'Description' })
    ).toBeInTheDocument()
    expect(
      screen.getByText('A great description for a great offer')
    ).toBeInTheDocument()
  })

  it('should not display the description section if the offer has no description', () => {
    renderAdageOfferDetailsSection({
      offer: {
        ...defaultCollectiveTemplateOffer,
        description: undefined,
      },
    })

    expect(
      screen.queryByRole('heading', { name: 'Description' })
    ).not.toBeInTheDocument()
  })
})
