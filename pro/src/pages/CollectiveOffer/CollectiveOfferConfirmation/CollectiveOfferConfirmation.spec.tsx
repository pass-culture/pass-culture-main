import { screen, waitForElementToBeRemoved } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import {
  defaultEducationalInstitution,
  getCollectiveOfferFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

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

const collectiveOfferTemplate = getCollectiveOfferFactory({
  id: mockedOfferId,
  isTemplate: true,
  displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
})

const renderCollectiveOfferCreation = async (
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(<CollectiveOfferConfirmation />, { ...options })
  await waitForElementToBeRemoved(() => screen.getByTestId('spinner'))
}

describe('CollectiveOfferConfirmation', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValue(
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
  })

  it('should render confirmation page when offer is pending', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      getCollectiveOfferFactory({
        id: mockedOfferId,
        isTemplate: false,
        displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
      })
    )
    await renderCollectiveOfferCreation()

    expect(
      screen.getByRole('heading', {
        name: 'Offre en cours de validation !',
      })
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to an institution', async () => {
    await renderCollectiveOfferCreation()

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
    await renderCollectiveOfferCreation()

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
    await renderCollectiveOfferCreation()

    expect(
      screen.getByRole('heading', {
        name: 'Votre offre a été publiée sur ADAGE',
      })
    ).toBeInTheDocument()
  })

  it('should render banner at the bottom of the page', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      collectiveOfferTemplate
    )
    await renderCollectiveOfferCreation()

    expect(
      screen.getByText('Quelle est la prochaine étape ?')
    ).toBeInTheDocument()
  })

  it('should link to /offres/vitrines when offer is template', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      collectiveOfferTemplate
    )
    await renderCollectiveOfferCreation()

    const link = screen.getByRole('link', { name: /voir mes offres/i })
    expect(link).toHaveAttribute('href', '/offres/vitrines')
  })

  it('should link to /offres/collectives when isShowcase is false', async () => {
    await renderCollectiveOfferCreation()
    const link = screen.getByRole('link', { name: /voir mes offres/i })
    expect(link).toHaveAttribute('href', '/offres/collectives')
  })

  it('should display ShareTemplateOfferLink when feature flag WIP_ENABLE_COLLECTIVE_OFFER_TEMPLATE_SHARE_LINK is enabled and offer is template', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      collectiveOfferTemplate
    )
    await renderCollectiveOfferCreation({
      features: ['WIP_ENABLE_COLLECTIVE_OFFER_TEMPLATE_SHARE_LINK'],
    })

    expect(screen.getByText('Créer une offre')).toBeInTheDocument()
    expect(screen.getByText('Offre de test')).toBeInTheDocument()
    expect(screen.getByText('Lien de l’offre')).toBeInTheDocument()
  })

  it('should not display ShareTemplateOfferLink when feature flag WIP_ENABLE_COLLECTIVE_OFFER_TEMPLATE_SHARE_LINK is disabled and offer is template', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValueOnce(
      collectiveOfferTemplate
    )
    await renderCollectiveOfferCreation()

    expect(screen.queryByText('Créer une offre')).not.toBeInTheDocument()
    expect(screen.queryByText('Offre de test')).not.toBeInTheDocument()
    expect(screen.queryByText('Lien de l’offre')).not.toBeInTheDocument()
  })
})
