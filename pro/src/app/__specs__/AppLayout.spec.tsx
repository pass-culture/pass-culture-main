import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import * as router from 'react-router-dom'

import { api } from 'apiClient/api'
import { SharedCurrentUserResponseModel } from 'apiClient/v1'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { AppLayout } from '../AppLayout'

vi.mock('apiClient/api', () => ({
  api: {
    listOfferersNames: vi.fn(),
    getOfferer: vi.fn(),
  },
}))

const renderApp = async (user: SharedCurrentUserResponseModel) => {
  renderWithProviders(
    <AppLayout>
      <p>Sub component</p>
    </AppLayout>,
    {
      user,
      initialRouterEntries: ['/'],
      storeOverrides: {
        user: {
          currentUser: user,
          selectedOffererId: 1,
        },
      },
    }
  )
  await waitFor(() => {
    expect(api.getOfferer).toHaveBeenCalled()
  })
}

describe('src | AppLayout', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOfferer').mockResolvedValue({
      ...defaultGetOffererResponseModel,
      isValidated: true,
    })

    vi.spyOn(router, 'useSearchParams').mockReturnValue([
      new URLSearchParams({ structure: '1' }),
      vi.fn(),
    ])

    window.addEventListener = vi.fn()
    window.removeEventListener = vi.fn()
  })

  describe('side navigation', () => {
    it('should render the new header when the WIP_ENABLE_PRO_SIDE_NAV is active', async () => {
      await renderApp(
        sharedCurrentUserFactory({
          navState: {
            newNavDate: '2021-01-01',
          },
        })
      )

      expect(screen.getByTitle('Profil')).toBeInTheDocument()
      expect(screen.queryByAltText('Menu')).not.toBeInTheDocument()
    })

    it('should display review banner if user has new nav active', async () => {
      await renderApp(
        sharedCurrentUserFactory({
          navState: {
            newNavDate: '2021-01-01',
            eligibilityDate: '2021-01-01',
          },
        })
      )

      expect(
        screen.getByRole('button', { name: 'Je donne mon avis' })
      ).toBeInTheDocument()
    })

    it('should not display review banner if user has new nav active but is not eligible (from a/b test)', async () => {
      await renderApp(
        sharedCurrentUserFactory({
          navState: {
            newNavDate: '2021-01-01',
            eligibilityDate: null,
          },
        })
      )

      expect(
        screen.queryByRole('button', { name: 'Je donne mon avis' })
      ).not.toBeInTheDocument()
    })

    describe('on smaller screen sizes', () => {
      beforeEach(async () => {
        await renderApp(
          sharedCurrentUserFactory({
            navState: {
              newNavDate: '2021-01-01',
            },
            hasPartnerPage: true,
          })
        )

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
        const NB_ITEMS_IN_NAV = 12
        for (let i = 0; i < NB_ITEMS_IN_NAV; i++) {
          await userEvent.tab()
        }
        expect(screen.getByLabelText('Fermer')).toHaveFocus()
      })
    })
  })
})
