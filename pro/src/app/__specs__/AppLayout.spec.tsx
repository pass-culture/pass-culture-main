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
    it('should render the new header when the WIP_ENABLE_PRO_SIDE_NAV is active', () => {
      options.features = ['WIP_ENABLE_PRO_SIDE_NAV']
      options.storeOverrides.user.currentUser.navState = {
        newNavDate: '2021-01-01',
      }
      renderApp(props, options)

      expect(screen.getByText('Se déconnecter')).toBeInTheDocument()
      expect(screen.queryByAltText('Menu')).not.toBeInTheDocument()
    })

    describe('on smaller screen sizes', () => {
      beforeEach(() => {
        options.features = ['WIP_ENABLE_PRO_SIDE_NAV']
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

      it('should focus the close button when the button menu is clicked', () => {
        userEvent.click(screen.getByLabelText('Menu'))

        waitFor(() => {
          expect(screen.getByLabelText('Fermer')).toHaveFocus()
        })
      })
    })
  })
})
