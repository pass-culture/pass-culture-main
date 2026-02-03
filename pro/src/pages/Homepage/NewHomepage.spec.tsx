import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { defaultDMSApplicationForEAC } from '@/commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererVenueResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { NewHomepage } from './NewHomepage'

const renderNewHomepage = (options?: RenderWithProvidersOptions) => {
  const user = sharedCurrentUserFactory()
  return renderWithProviders(<NewHomepage />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
        selectedVenue: defaultGetOffererVenueResponseModel,
      },
    },
    ...options,
  })
}

describe('NewHomepage', () => {
  it('should display the selected venue public name in the title', () => {
    renderNewHomepage()
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Votre espace Nom public de la structure'
    )
  })

  describe('Tabs', () => {
    it.each`
      scenario | allowedOnAdage | hasActiveIndividualOffer | hasCollectiveDMS | shouldDisplayTabs
      ${1}     | ${true}        | ${true}                  | ${true}          | ${true}
      ${2}     | ${true}        | ${true}                  | ${false}         | ${true}
      ${3}     | ${false}       | ${true}                  | ${true}          | ${true}
      ${4}     | ${false}       | ${true}                  | ${false}         | ${false}
      ${5}     | ${false}       | ${false}                 | ${true}          | ${false}
      ${6}     | ${true}        | ${false}                 | ${false}         | ${false}
    `(
      'should display tabs: $shouldDisplayTabs on scenario $scenario',
      ({
        allowedOnAdage,
        hasActiveIndividualOffer,
        hasCollectiveDMS,
        shouldDisplayTabs,
      }) => {
        renderNewHomepage({
          storeOverrides: {
            user: {
              selectedVenue: {
                ...defaultGetOffererVenueResponseModel,
                allowedOnAdage,
                hasActiveIndividualOffer,
                collectiveDmsApplications: hasCollectiveDMS
                  ? [defaultDMSApplicationForEAC]
                  : undefined,
              },
            },
          },
        })

        if (shouldDisplayTabs) {
          expect(screen.queryByRole('tablist')).toBeInTheDocument()
        } else {
          expect(screen.queryByRole('tablist')).not.toBeInTheDocument()
        }
      }
    )

    it('should render without accessibility violation', async () => {
      const { container } = renderNewHomepage({
        storeOverrides: {
          user: {
            selectedVenue: {
              ...defaultGetOffererVenueResponseModel,
              allowedOnAdage: true,
              hasActiveIndividualOffer: true,
            },
          },
        },
      })

      expect(await axe(container)).toHaveNoViolations()
    })

    it('should display the corresponding panel when click on a given tab', async () => {
      const user = userEvent.setup()
      renderNewHomepage({
        storeOverrides: {
          user: {
            selectedVenue: {
              ...defaultGetOffererVenueResponseModel,
              allowedOnAdage: true,
              hasActiveIndividualOffer: true,
            },
          },
        },
      })

      await user.click(screen.getByRole('tab', { name: /Collectif/ }))
      expect(screen.getByRole('tabpanel', { name: /Collectif/ })).toBeVisible()
      expect(
        screen.queryByRole('tabpanel', { name: /Individuel/ })
      ).not.toBeInTheDocument()

      await user.click(screen.getByRole('tab', { name: /Individuel/ }))
      expect(
        screen.queryByRole('tabpanel', { name: /Collectif/ })
      ).not.toBeInTheDocument()
      expect(screen.getByRole('tabpanel', { name: /Individuel/ })).toBeVisible()
    })
  })
})
