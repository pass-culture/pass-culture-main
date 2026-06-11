import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'

import { apiNew } from '@/apiClient/api'
import type {
  GetCollectiveOfferResponseModel,
  PatchCollectiveOfferBodyModel,
} from '@/apiClient/v1/new'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferInformations } from './CollectiveOfferInformations'
import { CollectiveOfferInformationsForm } from './components/CollectiveOfferInformationsForm/CollectiveOfferInformationsForm'

vi.mock('@/apiClient/api', () => ({ apiNew: { editCollectiveOffer: vi.fn() } }))

vi.mock(
  './components/CollectiveOfferInformationsForm/CollectiveOfferInformationsForm',
  () => ({
    CollectiveOfferInformationsForm: vi.fn(() => (
      <div data-testid="infos-form" />
    )),
  })
)

const setSubmitResponse = (partialOffer: PatchCollectiveOfferBodyModel) => {
  vi.mocked(CollectiveOfferInformationsForm).mockImplementationOnce(
    vi.fn(({ saveAndContinue }) => {
      return (
        <button onClick={() => saveAndContinue(partialOffer)}>
          Enregistrer
        </button>
      )
    })
  )
}

const renderCollectiveStockCreation = (
  offer: GetCollectiveOfferResponseModel,
  isCreation: boolean = true
) => {
  let path = `/offre/${offer.id}/collectif/stocks`
  if (!isCreation) {
    path += '/edition'
  }
  const venue = makeGetVenueResponseModel({ id: 1, allowedOnAdage: true })
  return renderWithProviders(<CollectiveOfferInformations offer={offer} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: venue,
      },
    },
  })
}

describe('<CollectiveOfferInformations />', () => {
  it('should render CollectiveOfferInformationsForm', () => {
    const offer = getCollectiveOfferFactory()
    renderCollectiveStockCreation(offer)

    expect(screen.getByTestId('infos-form')).toBeVisible()
  })

  it('should patch the offer', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory()
    setSubmitResponse({ contactEmail: 'test@email.com' })
    renderCollectiveStockCreation(offer)
    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(apiNew.editCollectiveOffer).toHaveBeenCalledExactlyOnceWith({
      path: { offer_id: offer.id },
      body: { contactEmail: 'test@email.com' },
    })
  })
})
