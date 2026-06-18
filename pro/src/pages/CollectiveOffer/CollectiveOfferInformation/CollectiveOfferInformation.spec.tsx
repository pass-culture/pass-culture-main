import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'

import { apiNew } from '@/apiClient/api'
import { ApiError } from '@/apiClient/compat'
import type {
  GetCollectiveOfferResponseModel,
  PatchCollectiveOfferBodyModel,
} from '@/apiClient/v1/new'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferInformation } from './CollectiveOfferInformation'
import { CollectiveOfferInformationForm } from './components/CollectiveOfferInformationForm/CollectiveOfferInformationForm'

const { editOfferMock, mockSnackBarSuccess, mockSnackBarError } = vi.hoisted(
  () => ({
    editOfferMock: vi.fn(),
    mockSnackBarSuccess: vi.fn(),
    mockSnackBarError: vi.fn(),
  })
)
vi.mock('@/apiClient/api', () => ({
  apiNew: { editCollectiveOffer: editOfferMock },
}))

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: () => ({
    success: mockSnackBarSuccess,
    error: mockSnackBarError,
  }),
}))
const mockNavigate = vi.fn()
vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(() => mockNavigate),
}))

vi.mock(
  './components/CollectiveOfferInformationForm/CollectiveOfferInformationForm',
  () => ({
    CollectiveOfferInformationForm: vi.fn(() => (
      <div data-testid="infos-form" />
    )),
  })
)

const goBackLinkVerificationMock = vi.fn()
const catchApiErrorVerificationMock = vi.fn()
const setSubmitResponse = (partialOffer: PatchCollectiveOfferBodyModel) => {
  vi.mocked(CollectiveOfferInformationForm).mockImplementationOnce(
    vi.fn(({ saveAndContinue, goBackLink }) => {
      goBackLinkVerificationMock(goBackLink)
      return (
        <button
          onClick={async () => {
            try {
              await saveAndContinue(partialOffer)
            } catch (e) {
              catchApiErrorVerificationMock(e)
            }
          }}
        >
          Enregistrer
        </button>
      )
    })
  )
}

const renderCollectiveOfferInformation = (
  offer: GetCollectiveOfferResponseModel,
  isEdition: boolean = false,
  hasRequete: boolean = false
) => {
  let path = `/offre/${offer.id}/collectif/stocks`
  if (isEdition) {
    path += '/edition'
  }
  if (hasRequete) {
    path += '?requete=1'
  }
  const venue = makeGetVenueResponseModel({ id: 1, allowedOnAdage: true })
  return renderWithProviders(<CollectiveOfferInformation offer={offer} />, {
    initialRouterEntries: [path],
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: venue,
      },
    },
  })
}

describe('<CollectiveOfferInformation />', () => {
  it('should render CollectiveOfferInformationForm', () => {
    const offer = getCollectiveOfferFactory()
    renderCollectiveOfferInformation(offer)

    expect(screen.getByTestId('infos-form')).toBeVisible()
  })

  it('should patch the offer on for submition', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory()
    setSubmitResponse({ contactEmail: 'test@email.com' })
    renderCollectiveOfferInformation(offer)

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(apiNew.editCollectiveOffer).toHaveBeenCalledExactlyOnceWith({
      path: { offer_id: offer.id },
      body: { contactEmail: 'test@email.com' },
    })
    expect(mockSnackBarSuccess).toHaveBeenCalledExactlyOnceWith(
      'Vos modifications ont bien été enregistrées'
    )
  })

  it('should show pass along API errors 4** to the form', async () => {
    const user = userEvent.setup()
    const error = new ApiError('', 400, 'Bad Request', {
      contactEmail: ["L'email est invalide"],
    })
    vi.mocked(apiNew.editCollectiveOffer).mockRejectedValueOnce(error)
    vi.spyOn(console, 'error').mockImplementationOnce(() => {})

    const offer = getCollectiveOfferFactory()
    setSubmitResponse({ contactEmail: 'test@email' })
    renderCollectiveOfferInformation(offer)

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(apiNew.editCollectiveOffer).toHaveBeenCalledExactlyOnceWith({
      path: { offer_id: offer.id },
      body: { contactEmail: 'test@email' },
    })
    expect(console.error).not.toHaveBeenCalled()
    expect(mockSnackBarError).not.toHaveBeenCalled()
    expect(mockSnackBarSuccess).not.toHaveBeenCalled()
    expect(mockNavigate).not.toHaveBeenCalled()
    expect(catchApiErrorVerificationMock).toHaveBeenCalledExactlyOnceWith(
      expect.objectContaining({
        message: '400 Bad Request',
        body: {
          contactEmail: ["L'email est invalide"],
        },
      })
    )
  })

  it('should log the other errors and display a snackbar', async () => {
    const user = userEvent.setup()
    const error = new Error('Something happened')
    vi.mocked(apiNew.editCollectiveOffer).mockRejectedValueOnce(error)
    vi.spyOn(console, 'error').mockImplementationOnce(() => {})

    const offer = getCollectiveOfferFactory()
    setSubmitResponse({ contactEmail: 'test@email' })
    renderCollectiveOfferInformation(offer)

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(console.error).toHaveBeenCalledExactlyOnceWith(
      expect.objectContaining({ message: 'Something happened' })
    )
    expect(mockSnackBarError).toHaveBeenCalledExactlyOnceWith(
      "Une erreur est survenue lors de l'enregistrement de votre offre."
    )
    expect(mockSnackBarSuccess).not.toHaveBeenCalled()
    expect(mockNavigate).not.toHaveBeenCalled()
    expect(catchApiErrorVerificationMock).not.toHaveBeenCalled()
  })

  it('on creation : should handle previous and next steps correctly', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory()
    const isEdition = false
    setSubmitResponse({ contactEmail: 'test@email.com' })
    renderCollectiveOfferInformation(offer, isEdition)

    expect(goBackLinkVerificationMock).toHaveBeenCalledWith(
      `/offre/${offer.id}/collectif/stocks`
    )
    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(mockNavigate).toHaveBeenCalledWith(
      `/offre/${offer.id}/collectif/etablissement`
    )
  })

  it('on creation : should pass along requestiId parameters to previous and next steps', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory()
    const isEdition = false
    const hasRequete = true
    setSubmitResponse({ contactEmail: 'test@email.com' })
    renderCollectiveOfferInformation(offer, isEdition, hasRequete)

    expect(goBackLinkVerificationMock).toHaveBeenCalledWith(
      `/offre/${offer.id}/collectif/stocks?requete=1`
    )
    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(mockNavigate).toHaveBeenCalledWith(
      `/offre/${offer.id}/collectif/etablissement?requete=1`
    )
  })

  it('on edition : should handle previous and next steps correctly', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory()
    const isEdition = true
    setSubmitResponse({ contactEmail: 'test@email.com' })
    renderCollectiveOfferInformation(offer, isEdition)

    expect(goBackLinkVerificationMock).toHaveBeenCalledWith(
      `/offre/${offer.id}/collectif/recapitulatif`
    )
    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(mockNavigate).toHaveBeenCalledWith(
      `/offre/${offer.id}/collectif/recapitulatif`
    )
  })
})
