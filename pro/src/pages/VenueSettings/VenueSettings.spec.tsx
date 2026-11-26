import { screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { STEP_ID_GENERAL_INFORMATIONS } from '@/components/SettingsTabs/constants'
import { getPanelId, getTabId } from '@/ui-kit/Tabs/Tabs'

import { VenueSettings } from './VenueSettings'

const selectedPartnerVenue = makeGetVenueResponseModel({ id: 1 })

const renderVenueSettings = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()

  return renderWithProviders(<VenueSettings />, {
    user,
    // In the app, each child route renders the tabpanel controlled by the selected tab
    routes: [
      {
        path: '/parametres',
        element: <VenueSettings />,
        children: [
          {
            path: STEP_ID_GENERAL_INFORMATIONS,
            element: (
              <div
                id={getPanelId(STEP_ID_GENERAL_INFORMATIONS)}
                role="tabpanel"
                aria-labelledby={getTabId(STEP_ID_GENERAL_INFORMATIONS)}
              />
            ),
          },
        ],
      },
    ],
    initialRouterEntries: [`/parametres/${STEP_ID_GENERAL_INFORMATIONS}`],
    ...options,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedPartnerVenue,
      },
      ...options?.storeOverrides,
    },
  })
}

describe('VenueSettings', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderVenueSettings()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the settings page heading', () => {
    renderVenueSettings()

    expect(
      screen.getByRole('heading', { name: 'Paramètres', level: 1 })
    ).toBeInTheDocument()
  })
})
