import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach } from 'vitest'

import { Events } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { ShareLink, type ShareLinkProps } from './ShareLink'

const logEventMock = vi.fn()
vi.mock('@/app/App/analytics/firebase', () => ({
  useAnalytics: () => ({ logEvent: logEventMock }),
}))

const renderShareLink = ({
  link,
  label,
  notifySuccessMessage,
  offerId,
}: ShareLinkProps) => {
  return renderWithProviders(
    <>
      <ShareLink
        link={link}
        label={label}
        notifySuccessMessage={notifySuccessMessage}
        offerId={offerId}
      />
      <SnackBarContainer />
    </>
  )
}

const link = 'https://passculture.education/partage/offre/1234'
const label = 'Lien de partage'
const notifySuccessMessage = 'Le lien ADAGE a bien été copié'
const offerId = 1

describe('ShareLink Component', () => {
  beforeEach(() => {
    document.execCommand = vi.fn()
  })

  it('should render the input with the correct value and label', () => {
    renderShareLink({ link, label, notifySuccessMessage, offerId })
    const input = screen.getByLabelText(label)
    expect(input).toHaveValue(link)
  })

  it('should render the copy button', () => {
    renderShareLink({ link, label, notifySuccessMessage, offerId })
    const button = screen.getByRole('button', { name: /Copier/i })
    expect(button).toBeInTheDocument()
  })

  it('should copy the link and show notification on button click', async () => {
    renderShareLink({ link, label, notifySuccessMessage, offerId })
    const button = screen.getByRole('button', { name: /Copier/i })
    await userEvent.click(button)
    expect(await screen.findByText(notifySuccessMessage)).toBeInTheDocument()
  })

  it('should copy the link to clipboard', async () => {
    const writeTextMock = vi.fn().mockResolvedValueOnce(undefined)
    Object.assign(navigator, {
      clipboard: { writeText: writeTextMock },
    })

    renderShareLink({ link, label, notifySuccessMessage, offerId })
    const button = screen.getByRole('button', { name: /Copier/i })
    await userEvent.click(button)
    expect(writeTextMock).toHaveBeenCalledWith(link)
  })

  it('should log event when link is copied', async () => {
    const writeTextMock = vi.fn().mockResolvedValueOnce(undefined)
    Object.assign(navigator, {
      clipboard: { writeText: writeTextMock },
    })

    renderShareLink({ link, label, notifySuccessMessage, offerId })
    const button = screen.getByRole('button', { name: /Copier/i })
    await userEvent.click(button)
    await userEvent.click(button)
    await userEvent.click(button)

    expect(logEventMock).toHaveBeenCalledTimes(1)
    expect(logEventMock).toHaveBeenCalledWith(
      Events.CLICKED_COPY_TEMPLATE_OFFER_LINK,
      {
        from: '/',
        offerId,
      }
    )
  })
})
