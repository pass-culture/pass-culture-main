import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { apiAdage } from 'apiClient/api'
import { Notification } from 'components/Notification/Notification'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import { defaultAdageUser } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PrebookingButton, PrebookingButtonProps } from '../PrebookingButton'

vi.mock('pages/AdageIframe/libs/initAlgoliaAnalytics')

vi.mock('apiClient/api', () => ({
  apiAdage: {
    bookCollectiveOffer: vi.fn(),
    logBookingModalButtonClick: vi.fn(),
  },
}))

vi.mock('utils/config', async () => {
  return {
    ...(await vi.importActual('utils/config')),
    LOGS_DATA: true,
  }
})

const renderPrebookingButton = (props: PrebookingButtonProps) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <PrebookingButton {...props} />
      <Notification />
    </AdageUserContextProvider>
  )
}

describe('offer item', () => {
  let props: PrebookingButtonProps

  beforeEach(() => {
    props = {
      canPrebookOffers: true,
      offerId: 1,
      queryId: 'aez',
      stock: {
        id: 117,
        startDatetime: '03/01/2023',
        bookingLimitDatetime: '01/01/2023',
        isBookable: true,
        price: 20,
        numberOfTickets: 3,
        educationalPriceDetail: '1200',
      },
    }
  })

  it('should not display when prebooking is not activated', () => {
    renderPrebookingButton({
      ...props,
      canPrebookOffers: false,
    })

    expect(screen.queryByText('Préréserver l’offre')).not.toBeInTheDocument()
  })

  it('should display when prebooking is activated', () => {
    renderPrebookingButton({ ...props })

    expect(screen.getByText('Préréserver l’offre')).toBeInTheDocument()
  })

  it('should display modal on click', async () => {
    renderPrebookingButton({ ...props })

    const preBookButton = screen.getByRole('button', {
      name: 'Préréserver l’offre',
    })
    await userEvent.click(preBookButton)

    expect(
      screen.getByText('Êtes-vous sûr de vouloir préréserver ?')
    ).toBeInTheDocument()
  })

  it('should display error message if uai does not match', async () => {
    renderPrebookingButton({ ...props })

    const preBookButton = screen.getByRole('button', {
      name: 'Préréserver l’offre',
    })
    await userEvent.click(preBookButton)

    expect(
      screen.getByText('Êtes-vous sûr de vouloir préréserver ?')
    ).toBeInTheDocument()

    vi.spyOn(apiAdage, 'bookCollectiveOffer').mockRejectedValueOnce({
      statusCode: 400,
      body: { code: 'WRONG_UAI_CODE' },
    })
    await userEvent.click(screen.getByRole('button', { name: 'Préréserver' }))

    expect(
      screen.getByText(
        'Cette offre n’est pas préréservable par votre établissement'
      )
    ).toBeInTheDocument()
  })

  it('should display a success message notification when booking worked', async () => {
    vi.spyOn(apiAdage, 'bookCollectiveOffer').mockResolvedValue({
      bookingId: 123,
    })

    renderPrebookingButton({ ...props })

    const preBookButton = screen.getByRole('button', {
      name: 'Préréserver l’offre',
    })
    await userEvent.click(preBookButton)

    expect(
      screen.getByText('Êtes-vous sûr de vouloir préréserver ?')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Préréserver' }))

    expect(
      screen.getByText('Votre préréservation a été effectuée avec succès')
    ).toBeInTheDocument()
  })

  it('should log info when clicking "préréserver" button ', async () => {
    renderPrebookingButton({ ...props, isInSuggestions: false })
    const preBookButton = screen.getByRole('button', {
      name: 'Préréserver l’offre',
    })
    await userEvent.click(preBookButton)

    expect(apiAdage.logBookingModalButtonClick).toHaveBeenCalledWith({
      iframeFrom: '/',
      isFromNoResult: false,
      queryId: 'aez',
      stockId: 117,
    })
  })

  it('should log info when clicking "préréserver" button for no result page suggestion', async () => {
    renderPrebookingButton({ ...props, isInSuggestions: true })

    const preBookButton = screen.getByRole('button', {
      name: 'Préréserver l’offre',
    })
    await userEvent.click(preBookButton)

    expect(apiAdage.logBookingModalButtonClick).toHaveBeenCalledWith({
      iframeFrom: '/',
      isFromNoResult: true,
      queryId: 'aez',
      stockId: 117,
    })
  })
})
