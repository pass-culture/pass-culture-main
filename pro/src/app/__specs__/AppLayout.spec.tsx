import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import AppLayout, { AppLayoutProps } from '../AppLayout'

const renderApp = async (
  props: AppLayoutProps,
  storeOverrides: any,
  url = '/'
) =>
  renderWithProviders(
    <AppLayout {...props}>
      <p>Sub component</p>
    </AppLayout>,
    { storeOverrides, initialRouterEntries: [url] }
  )

describe('src | AppLayout', () => {
  let props: AppLayoutProps
  let storeOverrides: any

  beforeEach(() => {
    props = {}
    storeOverrides = {
      user: { currentUser: { isAdmin: false } },
    }
  })

  it('should not render domain name banner when arriving from new domain name', async () => {
    // Given / When
    renderApp(props, storeOverrides)

    // Then
    await waitFor(() =>
      expect(
        screen.queryByText((content) =>
          content.startsWith('Notre nom de domaine évolue !')
        )
      ).not.toBeInTheDocument()
    )
  })

  it('should render domain name banner when coming from old domain name', async () => {
    // When
    renderApp(props, storeOverrides, '/?redirect=true')

    // Then
    await waitFor(() =>
      expect(
        screen.queryByText((content) =>
          content.startsWith('Notre nom de domaine évolue !')
        )
      ).toBeInTheDocument()
    )
  })
})
