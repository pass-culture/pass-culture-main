import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import * as reactRouter from 'react-router'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'
import {
  defaultEducationalInstitution,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
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

const collectiveOfferTemplate = getCollectiveOfferTemplateFactory({
  id: mockedOfferId,
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
        displayedStatus: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
      })
    )
    await renderCollectiveOfferCreation()

    expect(
      screen.getByText('Offre en cours de validation !')
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to an institution', async () => {
    await renderCollectiveOfferCreation()

    expect(
      screen.getByText('Votre offre a été publiée sur ADAGE')
    ).toBeInTheDocument()
    expect(
      screen.getByText('Collège Bellevue', { exact: false })
    ).toBeInTheDocument()
  })

  it('should render confirmation page when offer is not associated to an institution', async () => {
    vi.spyOn(api, 'getCollectiveOffer').mockResolvedValue(
      getCollectiveOfferFactory({
        displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
        institution: null,
      })
    )
    await renderCollectiveOfferCreation()

    expect(
      screen.getByText('Votre offre a été publiée sur ADAGE')
    ).toBeInTheDocument()
    expect(
      screen.queryByText('de l’établissement scolaire', { exact: false })
    ).not.toBeInTheDocument()
  })

  it('should render confirmation page when offer is active and associated to all institutions', async () => {
    await renderCollectiveOfferCreation()

    expect(
      screen.getByText('Votre offre a été publiée sur ADAGE')
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

  it('should link to /offres/collectives when isShowcase is false', async () => {
    await renderCollectiveOfferCreation()
    const link = screen.getByRole('link', { name: /voir mes offres/i })
    expect(link).toHaveAttribute('href', '/offres/collectives')
  })
})

describe('CollectiveOfferConfirmation - template', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(
      collectiveOfferTemplate
    )
    vi.spyOn(reactRouter, 'useParams').mockReturnValue({
      offerId: `T-${mockedOfferId}`,
    })
  })

  it('should display ShareTemplateOfferLink when offer is template', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValueOnce({
      ...collectiveOfferTemplate,
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_SHARE],
    })

    await renderCollectiveOfferCreation()

    expect(screen.getByText('Créer une offre')).toBeInTheDocument()
    expect(screen.getByText('Offre de test')).toBeInTheDocument()
    expect(screen.getByText('Lien de l’offre')).toBeInTheDocument()
  })

  it('should link to /offres/vitrines when offer is template', async () => {
    await renderCollectiveOfferCreation()

    const link = screen.getByRole('link', { name: /voir mes offres/i })
    expect(link).toHaveAttribute('href', '/offres/vitrines')
  })

  it('should not display institution when offer is template', async () => {
    await renderCollectiveOfferCreation()

    expect(screen.queryByText('établissement scolaire')).not.toBeInTheDocument()
  })
})
