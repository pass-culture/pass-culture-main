import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { apiAdage } from 'apiClient/api'
import { AdageUserContextProvider } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAdageUser,
  defaultCollectiveTemplateOffer,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { OfferShareLink, OfferShareLinkProps } from '../OfferShareLink'

vi.mock('apiClient/api', () => ({
  apiAdage: {
    logTrackingCtaShare: vi.fn(),
  },
}))

vi.mock('utils/config', async () => {
  return {
    ...(await vi.importActual('utils/config')),
    LOGS_DATA: true,
  }
})

const renderOfferShareLink = (props: OfferShareLinkProps) => {
  renderWithProviders(
    <AdageUserContextProvider adageUser={defaultAdageUser}>
      <OfferShareLink {...props} />
    </AdageUserContextProvider>
  )
}

describe('OfferShareLink', () => {
  const defaultProps: OfferShareLinkProps = {
    offer: { ...defaultCollectiveTemplateOffer, isTemplate: true },
  }

  it('should open email provider on click', () => {
    renderOfferShareLink(defaultProps)

    const shareLink = screen
      .getByRole('link', {
        name: /Partager par email/i,
      })
      .getAttribute('href')

    expect(shareLink).toContain('mailto')
  })

  it('should log a tracking event when clicking the share button', async () => {
    const logSpy = vi.spyOn(apiAdage, 'logTrackingCtaShare')
    renderOfferShareLink(defaultProps)

    const shareLink = screen.getByRole('link', {
      name: /Partager par email/i,
    })

    shareLink.addEventListener('click', (e) => {
      e.preventDefault()
    })

    await userEvent.click(shareLink)

    expect(logSpy).toHaveBeenCalled()
  })
})
