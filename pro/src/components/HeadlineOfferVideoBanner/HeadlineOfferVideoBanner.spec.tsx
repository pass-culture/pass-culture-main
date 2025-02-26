import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import * as useAnalytics from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'

import { HeadlineOfferVideoBanner } from './HeadlineOfferVideoBanner'

const mockLogEvent = vi.fn()

describe('HeadlineOfferVideoBanner', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  beforeEach(() => {
    Storage.prototype.setItem = vi.fn(() => 'false')
  })

  it('should render the banner with correct content', () => {
    const { getByText, getByTestId } = render(<HeadlineOfferVideoBanner />)

    // Check if the banner is rendered
    expect(getByTestId('awesome-banner')).toBeInTheDocument()

    // Check if the title and description are rendered
    expect(getByText(/Votre avis compte !/)).toBeInTheDocument()
    expect(
      getByText(
        'L’ajout de vidéo arrive bientôt ! Seriez-vous intéressé.e pour en ajouter sur vos offres ?'
      )
    ).toBeInTheDocument()

    // Check if the buttons are rendered
    expect(getByText('Intéressé.e')).toBeInTheDocument()
    expect(getByText('Pas intéressé.e')).toBeInTheDocument()
  })

  it('should log the correct event when "Intéressé.e" button is clicked', async () => {
    const { getByText } = render(<HeadlineOfferVideoBanner />)

    const interestedButton = getByText(/Intéressé.e/)

    await userEvent.click(interestedButton)

    // Ensure the event is logged with the correct parameters
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.FAKE_DOOR_VIDEO_INTERESTED,
      { answer: true }
    )
  })

  it('should log the correct event when "Pas intéressé.e" button is clicked', async () => {
    const { getByText } = render(<HeadlineOfferVideoBanner />)

    const notInterestedButton = getByText(/Pas intéressé.e/)

    await userEvent.click(notInterestedButton)

    // Ensure the event is logged with the correct parameters
    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.FAKE_DOOR_VIDEO_INTERESTED,
      { answer: false }
    )
  })

  it('uses localStorage value on initial render', () => {
    Storage.prototype.getItem = vi.fn(() => 'true')

    const { getByText } = render(<HeadlineOfferVideoBanner />)

    expect(getByText('Merci pour votre avis')).toBeInTheDocument()
  })
})
