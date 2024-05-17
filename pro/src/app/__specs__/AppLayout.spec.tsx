import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { AppLayout, AppLayoutProps } from '../AppLayout'

const renderApp = (
  props: AppLayoutProps,
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(
    <AppLayout {...props}>
      <p>Sub component</p>
    </AppLayout>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/'],
      ...options,
    }
  )

describe('src | AppLayout', () => {
  let props: AppLayoutProps

  describe('side navigation', () => {
    it('should render the new header when the WIP_ENABLE_PRO_SIDE_NAV is active', () => {
      renderApp(props, {
        user: sharedCurrentUserFactory({
          navState: {
            newNavDate: '2021-01-01',
          },
        }),
      })

      expect(screen.getByTitle('Profil')).toBeInTheDocument()
      expect(screen.queryByAltText('Menu')).not.toBeInTheDocument()
    })

    it('should display review banner if user has new nav active', () => {
      renderApp(props, {
        user: sharedCurrentUserFactory({
          navState: {
            newNavDate: '2021-01-01',
            eligibilityDate: '2021-01-01',
          },
        }),
      })

      expect(
        screen.getByRole('button', { name: 'Je donne mon avis' })
      ).toBeInTheDocument()
    })

    it('should not display review banner if user has new nav active but is not eligible (from a/b test)', () => {
      renderApp(props, {
        user: sharedCurrentUserFactory({
          navState: {
            newNavDate: '2021-01-01',
            eligibilityDate: null,
          },
        }),
      })

      expect(
        screen.queryByRole('button', { name: 'Je donne mon avis' })
      ).not.toBeInTheDocument()
    })

    describe('on smaller screen sizes', () => {
      beforeEach(() => {
        renderApp(props, {
          user: sharedCurrentUserFactory({
            navState: {
              newNavDate: '2021-01-01',
            },
            hasPartnerPage: true,
          }),
        })

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
})
