import { render, screen } from '@testing-library/react'

import { BannerPendingEmailValidation } from './BannerPendingEmailValidation'

describe('BannerPendingEmailValidation component', () => {
  it('should render a link to BannerPendingEmailValidation information when email is empty', () => {
    render(<BannerPendingEmailValidation email={''} />)
    const link = screen.getByRole('link', {
      name: /Je n’ai pas reçu le lien de confirmation/,
    })
    expect(link).toBeInTheDocument()

    expect(link).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/5723750427676'
    )
  })

  it('should render the email address in the banner text', () => {
    const email = 'test@example.com'
    render(<BannerPendingEmailValidation email={email} />)
    const emailElement = screen.getByText(email)
    expect(emailElement).toBeInTheDocument()
  })
})
