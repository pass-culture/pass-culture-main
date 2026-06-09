import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { apiNew } from '@/apiClient/api'
import {
  ApiError,
  type ApiRequestOptions,
  type ApiResult,
} from '@/apiClient/compat'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferTemplateAllowedAction,
  type GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1/new'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferTemplateEditionNavigation } from './CollectiveOfferTemplateEditionNavigation'

const mockSnackBar = {
  success: vi.fn(),
  error: vi.fn(),
}
vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => mockSnackBar,
}))

const mockAnalytics = { logEvent: vi.fn() }
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => mockAnalytics,
}))

const renderOfferTemplateEditionNavigation = (
  offer: GetCollectiveOfferTemplateResponseModel
) =>
  renderWithProviders(
    <CollectiveOfferTemplateEditionNavigation
      offer={offer}
      offerId={offer.id}
    />
  )

describe('<CollectiveOfferTemplateEditionNavigation />', () => {
  beforeEach(() => {
    vi.spyOn(apiNew, 'getCollectiveOfferTemplate').mockResolvedValue(
      getCollectiveOfferTemplateFactory()
    )

    vi.spyOn(apiNew, 'getVenues').mockResolvedValue({
      venues: [makeVenueListItem({ id: 2 })],
    })

    vi.spyOn(apiNew, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [],
    })

    vi.spyOn(apiNew, 'createCollectiveOffer').mockResolvedValue({ id: 1 })
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderOfferTemplateEditionNavigation(
      getCollectiveOfferTemplateFactory()
    )

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should log event when clicking "Dupliquer" button', async () => {
    const user = userEvent.setup()
    vi.spyOn(apiNew, 'duplicateCollectiveOffer').mockResolvedValueOnce(
      // Simuler la nouvelle offre dupliquée
      getCollectiveOfferFactory({
        id: 999,
      })
    )
    vi.spyOn(apiNew, 'attachOfferImage').mockResolvedValueOnce({
      imageUrl: 'my url',
    })

    fetchMock.mockResponseOnce((request) => {
      // Si l'offre mockée a cette URL, l'intercepter ici.
      if (
        request.url === 'https://example.com/image.jpg' &&
        request.method === 'GET'
      ) {
        return {
          status: 200,
          // Retourner un contenu simulé (ex: un faux buffer)
          body: 'Mock Image Data',
          headers: { 'Content-Type': 'image/jpeg' },
        }
      }
      return { status: 404 }
    })

    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_DUPLICATE],
    })
    renderOfferTemplateEditionNavigation(offer)

    await user.click(screen.getByRole('button', { name: 'Dupliquer' }))

    expect(mockAnalytics.logEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_DUPLICATE_BOOKABLE_OFFER,
      {
        offerId: offer.id,
        offerType: 'collective',
        offerStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
      }
    )
  })

  it('should show create bookable offer when CAN_CREATE_BOOKABLE_OFFER is allowed', () => {
    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
      ],
    })
    renderOfferTemplateEditionNavigation(offer)

    expect(
      screen.getByRole('button', { name: 'Créer une offre réservable' })
    ).toBeVisible()
  })

  it('should not show create bookable offer when CAN_CREATE_BOOKABLE_OFFER is not allowed', () => {
    const offer = getCollectiveOfferTemplateFactory({ allowedActions: [] })
    renderOfferTemplateEditionNavigation(offer)

    expect(
      screen.queryByRole('button', { name: 'Créer une offre réservable' })
    ).not.toBeInTheDocument()
  })

  it('should show duplicate button when CAN_DUPLICATE is allowed', () => {
    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_DUPLICATE],
    })
    renderOfferTemplateEditionNavigation(offer)

    expect(screen.getByRole('button', { name: 'Dupliquer' })).toBeVisible()
  })

  it('should return an error when the collective offer could not be retrieved', async () => {
    const user = userEvent.setup()
    vi.spyOn(apiNew, 'getCollectiveOfferTemplate').mockRejectedValueOnce(
      'error'
    )

    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
      ],
    })
    renderOfferTemplateEditionNavigation(offer)

    const duplicateOfferButton = screen.getByRole('button', {
      name: 'Créer une offre réservable',
    })
    await user.click(duplicateOfferButton)

    expect(mockSnackBar.error).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la récupération de votre offre'
    )
  })

  it('should show an error notification when the duplication failed', async () => {
    const user = userEvent.setup()
    vi.spyOn(apiNew, 'createCollectiveOffer').mockRejectedValueOnce(
      new ApiError({} as ApiRequestOptions, { status: 400 } as ApiResult, '')
    )

    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
      ],
    })
    renderOfferTemplateEditionNavigation(offer)

    await user.click(
      screen.getByRole('button', { name: 'Créer une offre réservable' })
    )

    expect(mockSnackBar.error).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
  })

  it('should return an error when trying to get offerer image', async () => {
    const user = userEvent.setup()
    // eslint-disable-next-line no-undef
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [
        CollectiveOfferTemplateAllowedAction.CAN_CREATE_BOOKABLE_OFFER,
      ],
    })
    renderOfferTemplateEditionNavigation(offer)

    await user.click(
      screen.getByRole('button', { name: 'Créer une offre réservable' })
    )

    expect(mockSnackBar.error).toHaveBeenCalledWith(
      'Impossible de dupliquer l’image'
    )
  })

  it('should show a success notification when archiving a template offer succeeds', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
    })
    renderOfferTemplateEditionNavigation(offer)

    await user.click(screen.getByRole('button', { name: 'Archiver' }))
    await user.click(screen.getByText('Archiver l’offre'))

    expect(mockSnackBar.success).toHaveBeenCalledWith(
      'Une offre a bien été archivée'
    )
  })

  it('should not see archive button archive action is not possible', () => {
    const offer = getCollectiveOfferTemplateFactory({ allowedActions: [] })
    renderOfferTemplateEditionNavigation(offer)

    expect(
      screen.queryByRole('button', { name: 'Archiver' })
    ).not.toBeInTheDocument()
  })

  it('should return an error on offer archiving when the offer id is not valid', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
    })
    renderOfferTemplateEditionNavigation({ ...offer, id: 0 })

    await user.click(screen.getByRole('button', { name: 'Archiver' }))
    await user.click(screen.getByText('Archiver l’offre'))

    expect(mockSnackBar.error).toHaveBeenNthCalledWith(
      1,
      "L'identifiant de l'offre n'est pas valide."
    )
  })

  it('should show an error notification when archive api call fails', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
    })
    renderOfferTemplateEditionNavigation(offer)

    vi.spyOn(
      apiNew,
      'patchCollectiveOffersTemplateArchive'
    ).mockRejectedValueOnce({})

    await user.click(screen.getByRole('button', { name: 'Archiver' }))
    await user.click(screen.getByText('Archiver l’offre'))

    expect(mockSnackBar.error).toHaveBeenCalledWith(
      "Une erreur est survenue lors de l'archivage de l'offre"
    )
  })

  it('should not show preview button when offer is template and status is archived', () => {
    const offer = getCollectiveOfferTemplateFactory({
      displayedStatus: CollectiveOfferDisplayedStatus.ARCHIVED,
    })
    renderOfferTemplateEditionNavigation(offer)

    expect(
      screen.queryByRole('button', { name: 'Aperçu dans ADAGE' })
    ).not.toBeInTheDocument()
  })

  it('should render share link drawer when pressing the share button', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferTemplateFactory({
      allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_SHARE],
    })
    renderOfferTemplateEditionNavigation(offer)

    const shareLinkButton = screen.getByRole('button', {
      name: 'Partager l’offre',
    })
    expect(shareLinkButton).toBeVisible()
    await user.click(shareLinkButton)

    expect(
      await screen.findByText(
        'Aidez les enseignants à retrouver votre offre plus facilement sur ADAGE'
      )
    ).toBeVisible()
  })
})
