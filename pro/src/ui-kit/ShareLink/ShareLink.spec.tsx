import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach } from 'vitest'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import { ShareLink, type ShareLinkProps } from './ShareLink'

const renderShareLink = ({
  link,
  label,
  notifySuccessMessage,
}: ShareLinkProps) => {
  return renderWithProviders(
    <>
      <ShareLink
        link={link}
        label={label}
        notifySuccessMessage={notifySuccessMessage}
      />
      <Notification />
    </>
  )
}

describe('ShareLink Component', () => {
  const link = 'https://passculture.education/partage/offre/1234'
  const label = 'Lien de partage'
  const notifySuccessMessage = 'Le lien ADAGE a bien été copié'

  beforeEach(() => {
    document.execCommand = vi.fn()
  })

  it('should render the input with the correct value and label', () => {
    renderShareLink({ link, label, notifySuccessMessage })
    const input = screen.getByLabelText(label)
    expect(input).toHaveValue(link)
  })

  it('should render the copy button', () => {
    renderShareLink({ link, label, notifySuccessMessage })
    const button = screen.getByRole('button', { name: /Copier/i })
    expect(button).toBeInTheDocument()
  })

  it('should copy the link and show notification on button click', async () => {
    renderShareLink({ link, label, notifySuccessMessage })
    const button = screen.getByRole('button', { name: /Copier/i })
    await userEvent.click(button)
    expect(await screen.findByText(notifySuccessMessage)).toBeInTheDocument()
  })

  it('should copy the link to clipboard', async () => {
    const writeTextMock = vi.fn().mockResolvedValueOnce(undefined)
    Object.assign(navigator, {
      clipboard: { writeText: writeTextMock },
    })

    renderShareLink({ link, label, notifySuccessMessage })
    const button = screen.getByRole('button', { name: /Copier/i })
    await userEvent.click(button)
    expect(writeTextMock).toHaveBeenCalledWith(link)
  })
})
