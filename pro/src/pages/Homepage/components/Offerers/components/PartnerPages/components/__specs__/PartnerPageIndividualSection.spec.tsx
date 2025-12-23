import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, vi } from 'vitest'

import { Events } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import {
  PartnerPageIndividualSection,
  type PartnerPageIndividualSectionProps,
} from '../PartnerPageIndividualSection'

const logEventMock = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: logEventMock }),
}))

const renderPartnerPageIndividualSection = (
  props: PartnerPageIndividualSectionProps
) => {
  return renderWithProviders(
    <>
      <PartnerPageIndividualSection {...props} />
      <SnackBarContainer />
    </>
  )
}

describe('PartnerPageIndividualSection', () => {
  beforeEach(() => {
    logEventMock.mockClear()
    document.execCommand = vi.fn()
  })

  it('should display right info when visible and title', () => {
    const props = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
    }

    renderPartnerPageIndividualSection(props)

    expect(screen.getByText('Grand public')).toBeInTheDocument()
    expect(screen.getByText('Copier le lien de la page')).toBeInTheDocument()
  })

  it('should display right info when is visible and in homepage', () => {
    const props: PartnerPageIndividualSectionProps = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
    }

    renderPartnerPageIndividualSection(props)

    expect(screen.getByText('Grand public')).toBeInTheDocument()
    expect(
      screen.getByText('Gérer votre page pour le grand public')
    ).toBeInTheDocument()
    expect(screen.getByText('Copier le lien de la page')).toBeInTheDocument()
  })

  it('should log event when clicking on preview venue link', async () => {
    const props: PartnerPageIndividualSectionProps = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
    }

    renderPartnerPageIndividualSection(props)

    const previewLink = screen.getByText('Voir votre page dans l’application')
    await userEvent.click(previewLink)

    expect(logEventMock).toHaveBeenCalledWith(
      Events.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK,
      {
        venueId: 7,
      }
    )
  })

  it('should copy venue link, show success message and log event when clicking on copy button', async () => {
    const writeTextMock = vi.fn().mockResolvedValueOnce(undefined)
    Object.assign(navigator, {
      clipboard: { writeText: writeTextMock },
    })

    const props: PartnerPageIndividualSectionProps = {
      venueId: 7,
      offererId: 8,
      venueName: 'Venue name',
    }

    renderPartnerPageIndividualSection(props)

    const copyButton = screen.getByText('Copier le lien de la page')
    await userEvent.click(copyButton)

    expect(writeTextMock).toHaveBeenCalledWith(
      expect.stringContaining('/lieu/7')
    )
    expect(await screen.findByText('Lien copié !')).toBeInTheDocument()
    expect(logEventMock).toHaveBeenCalledWith(
      Events.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK,
      {
        venueId: 7,
      }
    )
  })
})
