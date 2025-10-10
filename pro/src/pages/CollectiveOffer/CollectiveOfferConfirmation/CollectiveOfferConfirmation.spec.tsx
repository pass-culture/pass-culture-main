import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import {
  defaultEducationalInstitution,
  getCollectiveOfferFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Component as CollectiveOfferConfirmation } from './CollectiveOfferConfirmation'

const mockedOfferId = 1

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOffer: vi.fn(),
    getCollectiveOfferTemplate: vi.fn(),
  },
}))

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useParams: () => ({
    offerId: String(mockedOfferId),
  }),
}))

describe('CollectiveOfferConfirmation', () => {
  it('should render confirmation page when offer is pending', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      getCollectiveOfferFactory({
        id: mockedOfferId,
        isTemplate: false,
        displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
        institution: {
          ...defaultEducationalInstitution,
          name: 'Collège Bellevue',
        },
      })
    )

    renderWithProviders(<CollectiveOfferConfirmation />)
    await waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    expect(
      screen.getByRole('heading', {
        name: 'Offre en cours de validation !',
      })
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to an institution', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      getCollectiveOfferFactory({
        id: mockedOfferId,
        isTemplate: false,
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        institution: {
          ...defaultEducationalInstitution,
          name: 'Collège Bellevue',
        },
      })
    )

    renderWithProviders(<CollectiveOfferConfirmation />)
    await waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    expect(
      screen.getByRole('heading', {
        name: 'Votre offre a été publiée sur ADAGE',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByText('Collège Bellevue', { exact: false })
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to all institutions', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      getCollectiveOfferFactory({
        id: mockedOfferId,
        isTemplate: false,
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        institution: null,
      })
    )

    renderWithProviders(<CollectiveOfferConfirmation />)
    await waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    expect(
      screen.getByRole('heading', {
        name: 'Votre offre a été publiée sur ADAGE',
      })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'visible et réservable par les enseignants et chefs d’établissements',
        {
          exact: false,
        }
      )
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and template', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      getCollectiveOfferFactory({
        id: mockedOfferId,
        isTemplate: true,
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        institution: null,
      })
    )

    renderWithProviders(<CollectiveOfferConfirmation />)
    await waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    expect(
      screen.getByRole('heading', {
        name: 'Votre offre a été publiée sur ADAGE',
      })
    ).toBeInTheDocument()
  })

  it('should render banner at the bottom of the page', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      getCollectiveOfferFactory({
        id: mockedOfferId,
        isTemplate: true,
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        institution: null,
      })
    )

    renderWithProviders(<CollectiveOfferConfirmation />)
    await waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    expect(
      screen.getByText('Quelle est la prochaine étape ?')
    ).toBeInTheDocument()
  })

  it('should link to /offres/vitrines when offer is template', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      getCollectiveOfferFactory({
        id: mockedOfferId,
        isTemplate: true,
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        institution: null,
      })
    )

    renderWithProviders(<CollectiveOfferConfirmation />)
    await waitForElementToBeRemoved(() => screen.getByTestId('spinner'))

    const link = screen.getByRole('link', { name: /voir mes offres/i })
    expect(link).toHaveAttribute('href', '/offres/vitrines')
  })

  it('should link to /offres/collectives when isShowcase is false', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      getCollectiveOfferFactory({
        id: mockedOfferId,
        isTemplate: false,
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        institution: null,
      })
    )

    renderWithProviders(<CollectiveOfferConfirmation />, {
      features: [],
    })
    await waitForElementToBeRemoved(() => screen.getByTestId('spinner'))
    const link = screen.getByRole('link', { name: /voir mes offres/i })
    expect(link).toHaveAttribute('href', '/offres/collectives')
  })
})
