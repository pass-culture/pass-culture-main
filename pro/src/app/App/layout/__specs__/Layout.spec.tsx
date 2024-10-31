import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { defaultGetOffererResponseModel } from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { Layout } from '../Layout'

const renderLayout = (isImpersonated = false) => {
  renderWithProviders(<Layout />, {
    user: sharedCurrentUserFactory({
      isImpersonated,
    }),
  })
}

describe('Layout', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      isValidated: true,
    })

    window.addEventListener = vi.fn()
    window.removeEventListener = vi.fn()
  })

  describe('side navigation', () => {
    describe('on smaller screen sizes', () => {
      beforeEach(() => {
        renderLayout()

        global.innerWidth = 500
        global.dispatchEvent(new Event('resize'))
      })

      it('should render the button menu', () => {
        expect(screen.getByLabelText('Menu')).toBeInTheDocument()
      })

      it('should focus the close button when the button menu is clicked', async () => {
        await userEvent.click(screen.getByLabelText('Menu'))

        expect(screen.getByLabelText('Fermer')).toHaveFocus()
      })
      it('should trap focus when side nav is open', async () => {
        await userEvent.click(screen.getByLabelText('Menu'))

        expect(screen.getByLabelText('Fermer')).toHaveFocus()
        const NB_ITEMS_IN_NAV = 11
        for (let i = 0; i < NB_ITEMS_IN_NAV; i++) {
          await userEvent.tab()
        }
        expect(screen.getByLabelText('Fermer')).toHaveFocus()
      })
    })
  })

  it('should render connect as banner if user has isImpersonated value is true', () => {
    renderLayout(true)

    expect(
      screen.getByText('Vous êtes connecté en tant que :')
    ).toBeInTheDocument()
  })
})
