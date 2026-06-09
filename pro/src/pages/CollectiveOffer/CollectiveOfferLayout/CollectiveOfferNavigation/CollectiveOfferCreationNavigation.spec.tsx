import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferCreationNavigation,
  type CollectiveOfferCreationNavigationProps,
} from '../CollectiveOfferNavigation/CollectiveOfferCreationNavigation'
import { CollectiveOfferStep } from './constants'

const renderCollectiveOfferNavigation = (
  props: CollectiveOfferCreationNavigationProps
) => renderWithProviders(<CollectiveOfferCreationNavigation {...props} />)

describe('<CollectiveOfferCreationNavigation />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferStep.DETAILS,
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display navigation for collective offer in creation', async () => {
    renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferStep.DETAILS,
      offerId: 0,
    })

    expect(screen.getByTestId('stepper')).toBeVisible()

    const listItems = await screen.findAllByRole('listitem')

    expect(listItems).toHaveLength(5)
    expect(listItems[0]).toHaveTextContent("Détails de l'offre")
    expect(listItems[1]).toHaveTextContent('Dates et prix')
    expect(listItems[2]).toHaveTextContent('Établissement et enseignant')
    expect(listItems[3]).toHaveTextContent('Récapitulatif')
    expect(listItems[4]).toHaveTextContent('Aperçu')

    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(0)
  })

  it('should show links if institution is the active step', () => {
    const offer = getCollectiveOfferFactory({ institution: undefined })
    renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferStep.INSTITUTION,
      offer,
      offerId: offer.id,
    })
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(3)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offer.id}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/stocks`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/etablissement`
    )
  })

  it('should show links if summary is the active step', () => {
    const offer = getCollectiveOfferFactory({
      institution: {
        city: '',
        id: 1,
        institutionId: '2',
        name: '',
        phoneNumber: '',
        postalCode: '',
        institutionType: '',
      },
    })
    renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferStep.SUMMARY,
      offer,
      offerId: offer.id,
    })
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(5)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offer.id}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/stocks`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/etablissement`
    )
    expect(links[3].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/creation/recapitulatif`
    )
    expect(links[4].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/creation/apercu`
    )
  })

  it('should show links if confirmation is the active step', () => {
    const offer = getCollectiveOfferFactory({
      institution: {
        city: '',
        id: 1,
        institutionId: '2',
        name: '',
        phoneNumber: '',
        postalCode: '',
        institutionType: '',
      },
    })
    renderCollectiveOfferNavigation({
      activeStep: CollectiveOfferStep.CONFIRMATION,
      offer,
      offerId: offer.id,
    })
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(5)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offer.id}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/stocks`
    )
    expect(links[2].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/etablissement`
    )
    expect(links[3].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/creation/recapitulatif`
    )
  })

  it('should be able to go to the institution and stocks step if the institution and stock are already filled', () => {
    const offer = getCollectiveOfferFactory()
    renderCollectiveOfferNavigation({
      offerId: offer.id,
      offer,
      activeStep: CollectiveOfferStep.DETAILS,
    })

    expect(
      screen.getByRole('link', { name: /Établissement et enseignant/ })
    ).toBeVisible()
    expect(screen.getByRole('link', { name: /Dates et prix/ })).toBeVisible()
  })

  it('should be able to go to the stocks step if the details are already filled', () => {
    const offer = getCollectiveOfferFactory({
      institution: undefined,
      collectiveStock: undefined,
    })
    renderCollectiveOfferNavigation({
      offerId: offer.id,
      offer,
      activeStep: CollectiveOfferStep.DETAILS,
    })

    expect(
      screen.queryByRole('link', { name: /Établissement et enseignant/ })
    ).not.toBeInTheDocument()

    expect(screen.getByRole('link', { name: /Dates et prix/ })).toBeVisible()
  })
})
