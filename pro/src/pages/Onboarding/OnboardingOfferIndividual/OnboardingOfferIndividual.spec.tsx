import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import {
  screen,
  waitForElementToBeRemoved,
  within,
} from '@testing-library/react'
import * as useHasAccessToDidacticOnboarding from 'commons/hooks/useHasAccessToDidacticOnboarding'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
  listOffersOfferFactory,
} from 'commons/utils/factories/individualApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'

import {
  MAX_DRAFT_TO_DISPLAY,
  OnboardingOfferIndividual,
} from './OnboardingOfferIndividual'

const renderOnboardingOfferIndividual = (
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<OnboardingOfferIndividual />, { ...options })
}

vi.mock('apiClient/api', () => ({
  api: {
    listOffers: vi.fn(),
    getOfferer: vi.fn(),
  },
}))
vi.mock('commons/hooks/useHasAccessToDidacticOnboarding')
describe('<OnboardingOfferIndividual />', () => {
  beforeEach(() => {
    vi.spyOn(api, 'listOffers').mockResolvedValue([])
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      id: 42,
      managedVenues: [
        { ...defaultGetOffererVenueResponseModel, isPermanent: true, id: 1337 },
      ],
    })
    vi.spyOn(
      useHasAccessToDidacticOnboarding,
      'useHasAccessToDidacticOnboarding'
    ).mockResolvedValue(true)
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
    renderOnboardingOfferIndividual({
      storeOverrides: {
        offerer: {
          currentOfferer: {
            id: 42,
            isOnboarded: false,
          },
          offererNames: [],
        },
      },
    })

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getOfferer).toHaveBeenCalledOnce()

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
})
