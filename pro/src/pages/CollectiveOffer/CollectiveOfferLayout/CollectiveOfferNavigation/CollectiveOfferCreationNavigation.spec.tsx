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
  props: CollectiveOfferCreationNavigationProps,
  features: string[] = []
) =>
  renderWithProviders(<CollectiveOfferCreationNavigation {...props} />, {
    features,
  })

describe('<CollectiveOfferCreationNavigation />', () => {
  it('should render without accessibility violations', async () => {
    const activeStep = CollectiveOfferStep.DETAILS
    const { container } = renderCollectiveOfferNavigation({ activeStep })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display navigation for collective offer in creation', async () => {
    const activeStep = CollectiveOfferStep.DETAILS
    renderCollectiveOfferNavigation({ activeStep })

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
    const activeStep = CollectiveOfferStep.INSTITUTION
    const offer = getCollectiveOfferFactory({ institution: undefined })
    renderCollectiveOfferNavigation({ activeStep, offer })

    // Only the steps preceding the active one are navigable, the active step
    // never links to the page currently displayed.
    const links = screen.queryAllByRole('link')
    expect(links).toHaveLength(2)
    expect(links[0].getAttribute('href')).toBe(
      `/offre/collectif/${offer.id}/creation`
    )
    expect(links[1].getAttribute('href')).toBe(
      `/offre/${offer.id}/collectif/stocks`
    )
  })

  it('should show links if summary is the active step', () => {
    const activeStep = CollectiveOfferStep.SUMMARY
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
    renderCollectiveOfferNavigation({ activeStep, offer })

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

  it('should not display any link when the first step is the active one', () => {
    const activeStep = CollectiveOfferStep.DETAILS
    const offer = getCollectiveOfferFactory()
    renderCollectiveOfferNavigation({ activeStep, offer })

    expect(screen.queryAllByRole('link')).toHaveLength(0)
  })

  it('should be able to go back to the institution and stocks step if the institution and stock are already filled', () => {
    const activeStep = CollectiveOfferStep.PREVIEW
    const offer = getCollectiveOfferFactory()
    renderCollectiveOfferNavigation({ activeStep, offer })

    expect(
      screen.getByRole('link', { name: /Établissement et enseignant/ })
    ).toBeVisible()
    expect(screen.getByRole('link', { name: /Dates et prix/ })).toBeVisible()
  })

  it('should not link the institution step if the stocks are not filled', () => {
    const activeStep = CollectiveOfferStep.SUMMARY
    const offer = getCollectiveOfferFactory({
      institution: undefined,
      collectiveStock: undefined,
    })
    renderCollectiveOfferNavigation({ activeStep, offer })

    expect(
      screen.queryByRole('link', { name: /Établissement et enseignant/ })
    ).not.toBeInTheDocument()

    expect(screen.getByRole('link', { name: /Dates et prix/ })).toBeVisible()
  })

  describe('with WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS FF', () => {
    const features = ['WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS']

    it('should keep the Établissement step reachable when the institution is set but additional details are empty', () => {
      const activeStep = CollectiveOfferStep.SUMMARY
      const offer = getCollectiveOfferFactory({
        additionalDetails: null,
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

      renderCollectiveOfferNavigation({ activeStep, offer }, features)

      expect(
        screen.getByRole('link', { name: /Établissement et enseignant/ })
      ).toHaveAttribute('href', `/offre/${offer.id}/collectif/etablissement`)
    })

    it('should show the INFORMATIONS step', () => {
      const activeStep = CollectiveOfferStep.INSTITUTION
      const offer = getCollectiveOfferFactory()

      renderCollectiveOfferNavigation({ offer, activeStep }, features)

      const listItems = screen.getAllByRole('listitem')
      expect(listItems).toHaveLength(6)
      expect(listItems[0]).toHaveTextContent("Détails de l'offre")
      expect(listItems[1]).toHaveTextContent('Dates et prix')
      expect(listItems[2]).toHaveTextContent('Informations pratiques')
      expect(listItems[3]).toHaveTextContent('Établissement et enseignant')
      expect(listItems[4]).toHaveTextContent('Récapitulatif')
      expect(listItems[5]).toHaveTextContent('Aperçu')

      const links = screen.getAllByRole('link')
      expect(links).toHaveLength(3)
      expect(links[0].getAttribute('href')).toBe(
        `/offre/collectif/${offer.id}/creation`
      )
      expect(links[1].getAttribute('href')).toBe(
        `/offre/${offer.id}/collectif/stocks`
      )
      expect(links[2].getAttribute('href')).toBe(
        `/offre/${offer.id}/collectif/informations-pratiques`
      )
    })
  })
})
