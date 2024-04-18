import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { AppLayout, AppLayoutProps } from '../AppLayout'

const renderApp = (props: AppLayoutProps, options: any) =>
  renderWithProviders(
    <AppLayout {...props}>
      <p>Sub component</p>
    </AppLayout>,
    options
  )

describe('src | AppLayout', () => {
  let props: AppLayoutProps
  let options: any

  beforeEach(() => {
    props = {}
    options = {
      storeOverrides: {
        user: { currentUser: { isAdmin: false } },
      },
      initialRouterEntries: ['/'],
    }
  })

  it('should not render domain name banner when arriving from new domain name', async () => {
    renderApp(props, options)

    await waitFor(() =>
      expect(
        screen.queryByText((content) =>
          content.startsWith('Notre nom de domaine évolue !')
        )
      ).not.toBeInTheDocument()
    )
  })

  it('should render domain name banner when coming from old domain name', async () => {
    options.initialRouterEntries = ['/?redirect=true']
    renderApp(props, options)

    // Then
    await waitFor(() =>
      expect(
        screen.queryByText((content) =>
          content.startsWith('Notre nom de domaine évolue !')
        )
      ).toBeInTheDocument()
    )
  })

  describe('side navigation', () => {
    it('should render the header', () => {
      options.storeOverrides.user.currentUser.navState = {
        newNavDate: '2021-01-01',
      }
      renderApp(props, options)

      expect(screen.getByText('Se déconnecter')).toBeInTheDocument()
      expect(screen.queryByAltText('Menu')).not.toBeInTheDocument()
    })

    it('should display review banner if user has new nav active', () => {
      options.storeOverrides.user.currentUser.navState = {
        newNavDate: '2021-01-01',
        eligibilityDate: '2021-01-01',
      }
      renderApp(props, options)

      expect(
        screen.getByRole('button', { name: 'Je donne mon avis' })
      ).toBeInTheDocument()
    })

    it('should not display review banner if user has new nav active but is not eligible (from a/b test)', () => {
      options.storeOverrides.user.currentUser.navState = {
        newNavDate: '2021-01-01',
        eligibilityDate: null,
      }
      renderApp(props, options)

      expect(
        screen.queryByRole('button', { name: 'Je donne mon avis' })
      ).not.toBeInTheDocument()
    })

    describe('on smaller screen sizes', () => {
      beforeEach(() => {
        options.storeOverrides.user.currentUser.navState = {
          newNavDate: '2021-01-01',
        }
        renderApp(props, options)

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
