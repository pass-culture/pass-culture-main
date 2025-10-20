import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'

import { api } from '@/apiClient/api'
import { OfferStatus } from '@/apiClient/v1'
import {
  defaultGetOffererVenueResponseModel,
  listOffersOfferFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  MAX_DRAFT_TO_DISPLAY,
  OnboardingOfferIndividual,
} from './OnboardingOfferIndividual'

const renderOnboardingOfferIndividual = (
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<OnboardingOfferIndividual />, {
    ...options,
    ...{
      storeOverrides: {
        offerer: {
          currentOfferer: {
            id: 42,
            isOnboarded: false,
            managedVenues: [
              {
                ...defaultGetOffererVenueResponseModel,
                isPermanent: true,
                id: 1337,
              },
            ],
          },
          offererNames: [],
        },
      },
    },
  })
}

vi.mock('@/apiClient/api', () => ({
  api: {
    listOffers: vi.fn(),
    getOfferer: vi.fn(),
  },
}))

describe('<OnboardingOfferIndividual />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listOffers').mockResolvedValue([])
  })

  it('should propose how to create the 1st offer', async () => {
    renderOnboardingOfferIndividual()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      await screen.findByRole('heading', {
        name: /Comment souhaitez-vous créer votre 1ère offre ?/,
      })
    ).toBeInTheDocument()

    const links = await screen.findAllByText(/Manuellement|Automatiquement/)

    expect(links).toHaveLength(2)
  })

  it('should redirect to venue settings if user chooses "automatiquement"', async () => {
    renderOnboardingOfferIndividual()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      await screen.findByRole('link', { name: /Automatiquement/ })
    ).toHaveAttribute('href', '/structures/42/lieux/1337/parametres')
  })

  it('should not display drafts if listOffers returns an empty array', async () => {
    renderOnboardingOfferIndividual()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByRole('heading', {
        name: /Reprendre une offre déjà commencée/,
      })
    ).not.toBeInTheDocument()
  })

  it('should display drafts if there is any', async () => {
    vi.spyOn(api, 'listOffers').mockResolvedValue([
      listOffersOfferFactory({
        id: 1,
        name: 'Foo',
        status: OfferStatus.DRAFT,
      }),
      listOffersOfferFactory({
        id: 2,
        name: 'Bar',
        status: OfferStatus.DRAFT,
      }),
    ])

    renderOnboardingOfferIndividual()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(
      screen.queryByRole('heading', {
        name: /Reprendre une offre déjà commencée/,
      })
    ).toBeInTheDocument()

    expect(await screen.findAllByText(/Foo|Bar/)).toHaveLength(2)
  })

  it(`should not display over ${MAX_DRAFT_TO_DISPLAY} draft offers`, async () => {
    vi.spyOn(api, 'listOffers').mockResolvedValue([
      ...Array(MAX_DRAFT_TO_DISPLAY + 1)
        .fill(true)
        .map(() =>
          listOffersOfferFactory({
            status: OfferStatus.DRAFT,
          })
        ),
    ])

    renderOnboardingOfferIndividual()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    // Find all card links after that heading
    const cardLinks = within(screen.getByTestId('draft-offers')).getAllByTestId(
      'cardlink'
    )
    expect(cardLinks).toHaveLength(MAX_DRAFT_TO_DISPLAY)
  })

  it('should have a manyally create offer button that skips the offer type selection when the FF WIP_ENABLE_NEW_OFFER_CREATION_FLOW is enabled', async () => {
    renderOnboardingOfferIndividual({
      features: ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW'],
    })

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByRole('link', { name: 'Manuellement' })).toHaveAttribute(
      'href',
      '/onboarding/offre/individuelle/creation/description'
    )
  })

  it('should have a manyally create offer button that redirects to the offer type selection when the FF WIP_ENABLE_NEW_OFFER_CREATION_FLOW is disabled', async () => {
    renderOnboardingOfferIndividual()

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(screen.getByRole('link', { name: 'Manuellement' })).toHaveAttribute(
      'href',
      '/onboarding/offre/creation'
    )
  })
})
