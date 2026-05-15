import { screen } from '@testing-library/react'
import { Route, Routes } from 'react-router'

import { apiNew } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { EmailChangeValidation } from '@/pages/EmailChangeValidation/EmailChangeValidation'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    patchValidateEmail: vi.fn(),
  },
}))

const renderValidation = () => {
  return renderWithProviders(
    <Routes>
      <Route path="/" element={<EmailChangeValidation />} />
    </Routes>,
    { initialRouterEntries: ['/?token=123'] }
  )
}

describe('screens:EmailChangeValidation', () => {
  it('renders component successfully when success', async () => {
    vi.spyOn(apiNew, 'patchValidateEmail').mockResolvedValueOnce()
    renderValidation()

    expect(apiNew.patchValidateEmail).toHaveBeenCalledWith({
      body: { token: '123' },
    })

    expect(
      await screen.findByText(
        /Merci d’avoir confirmé votre changement d’adresse email./,
        {
          selector: 'p',
        }
      )
    ).toBeInTheDocument()
  })

  it('renders component successfully when not success', async () => {
    vi.spyOn(apiNew, 'patchValidateEmail').mockRejectedValueOnce({})
    renderValidation()
    expect(
      await screen.findByText(
        /Votre adresse email n’a pas été modifiée car le lien/,
        {
          selector: 'p',
        }
      )
    ).toBeInTheDocument()
  })
})
