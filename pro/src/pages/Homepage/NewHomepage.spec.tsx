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

import * as tabManagement from './commons/utils/tabsManagement'
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
          expect(screen.queryByRole('tablist')).toBeVisible()
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

    describe('initial tab', () => {
      it('should ask for initial tab on load and save the visited tab on tab change', async () => {
        vi.spyOn(tabManagement, 'getInitialTab').mockReturnValue(
          'tab-individual'
        )
        vi.spyOn(tabManagement, 'onNewTabSelected')

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

        expect(tabManagement.getInitialTab).toHaveBeenCalledOnce()
        expect(
          screen.getByRole('tabpanel', { name: /Individuel/ })
        ).toBeVisible()

        // It's not the Homepage component's role to save the first computed value
        // it's done in tabManagement module
        expect(tabManagement.onNewTabSelected).not.toHaveBeenCalled()

        await user.click(screen.getByRole('tab', { name: /Collectif/ }))
        expect(tabManagement.onNewTabSelected).toHaveBeenCalledWith(
          'tab-collective',
          defaultGetOffererVenueResponseModel.id
        )
      })

      it.each`
        scenario             | venue    | hasIndividual | hasCollective | initialTab
        ${'only collective'} | ${true}  | ${false}      | ${true}       | ${'collective'}
        ${'only individual'} | ${true}  | ${true}       | ${false}      | ${'individual'}
        ${'nothing'}         | ${true}  | ${false}      | ${false}      | ${'error'}
        ${'no venue '}       | ${false} | ${false}      | ${false}      | ${'error'}
      `(
        'should handle the $scenario case.',
        ({ venue, hasIndividual, hasCollective, initialTab }) => {
          vi.spyOn(tabManagement, 'getInitialTab').mockReturnValue(
            `tab-${initialTab}`
          )
          vi.spyOn(tabManagement, 'onNewTabSelected')

          renderNewHomepage({
            storeOverrides: {
              user: {
                selectedVenue: venue
                  ? {
                      ...defaultGetOffererVenueResponseModel,
                      allowedOnAdage: hasCollective,
                      hasActiveIndividualOffer: hasIndividual,
                    }
                  : null,
              },
            },
          })

          expect(tabManagement.getInitialTab).toHaveBeenCalledExactlyOnceWith(
            venue ? defaultGetOffererVenueResponseModel.id : null,
            hasIndividual,
            hasCollective
          )
          expect(screen.queryByRole('tab')).not.toBeInTheDocument()
          // It's not the Homepage component's role to save the first computed value
          // it's done in tabManagement module
          expect(tabManagement.onNewTabSelected).not.toHaveBeenCalled()
        }
      )
    })
  })
})
