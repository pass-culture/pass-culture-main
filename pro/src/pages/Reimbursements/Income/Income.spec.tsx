import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import type {
  AggregatedRevenueModel,
  StatisticsModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import * as useIsCaledonian from '@/commons/hooks/useIsCaledonian'
import * as convertEuroToPacificFranc from '@/commons/utils/convertEuroToPacificFranc'
import { makeVenueListItem } from '@/commons/utils/factories/individualApiFactories'
import { statisticsFactory } from '@/commons/utils/factories/statisticsFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { Income } from './Income'
import { IncomeResultsBox } from './IncomeResultsBox/IncomeResultsBox'
import { isCollectiveAndIndividualRevenue, isCollectiveRevenue } from './utils'

const MOCK_DATA: {
  selectedOffererId: number
  venues: VenueListItemResponseModel[]
} & StatisticsModel = {
  selectedOffererId: 100,
  venues: [
    makeVenueListItem({
      id: 1,
      isPermanent: true,
      hasCreatedOffer: true,
    }),
    makeVenueListItem({
      id: 2,
      isPermanent: true,
      hasCreatedOffer: true,
    }),
  ],
  ...statisticsFactory({
    emptyYear: '1994',
    individualRevenueOnlyYear: '1995',
    collectiveRevenueOnlyYear: '1996',
    collectiveAndIndividualRevenueYear: '1997',
    lastYear: '1997',
  }),
}

const LABELS = {
  error: /Erreur dans le chargement des données./,
  secondVenueSelector: /Nom public de la structure 2/,
  venuesSelectorError: /Vous devez sélectionner au moins un partenaire/,
  incomeResultsLabel: /Chiffre d’affaires total/,
  forecastIncomeResultLabel: /Chiffre d’affaires total prévisionnel/,
  emptyScreen: /Vous n’avez aucune réservation/,
  mandatoryHelper: /\* sont obligatoires/,
}

const renderIncome = () => {
  renderWithProviders(<Income />, {
    user: sharedCurrentUserFactory(),
    storeOverrides: {
      user: { currentUser: sharedCurrentUserFactory() },
      offerer: currentOffererFactory({
        currentOfferer: { id: MOCK_DATA.selectedOffererId },
      }),
    },
  })
}

vi.mock('@/apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
    getStatistics: vi.fn(),
  },
}))

describe('Income', () => {
  describe('when the page first renders', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: vi.fn(),
      }))
    })

    it('should attempt to fetch venues data and display a loading spinner meanwhile', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() =>
        expect(screen.getByTestId('venues-spinner')).toBeInTheDocument()
      )
      expect(api.getVenues).toHaveBeenNthCalledWith(
        1,
        true,
        null,
        MOCK_DATA.selectedOffererId
      )
    })

    it('should display an error message if venues couldnt be fetched', async () => {
      vi.spyOn(api, 'getVenues').mockRejectedValue(new Error('error'))
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() =>
        expect(screen.getByText(LABELS.error)).toBeInTheDocument()
      )
      expect(api.getVenues).toHaveBeenNthCalledWith(
        1,
        true,
        null,
        MOCK_DATA.selectedOffererId
      )
    })

    it('should display an empty screen if no venues were found', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() =>
        expect(screen.getByText(LABELS.emptyScreen)).toBeInTheDocument()
      )
      expect(api.getVenues).toHaveBeenNthCalledWith(
        1,
        true,
        null,
        MOCK_DATA.selectedOffererId
      )
    })

    it('should attempt to fetch income data with all venues and display a loading spinner meanwhile', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })

      renderIncome()

      await waitFor(() =>
        expect(screen.getByTestId('income-spinner')).toBeInTheDocument()
      )
      expect(api.getStatistics).toHaveBeenNthCalledWith(
        1,
        MOCK_DATA.venues.map((venue) => venue.id)
      )
    })

    it('should display an error message if income couldnt be fetched', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockRejectedValue(new Error('error'))
      renderIncome()

      await waitFor(() =>
        expect(screen.getByText(LABELS.error)).toBeInTheDocument()
      )
    })

    it('should display an empty screen if no income data was found', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({ incomeByYear: {} })
      renderIncome()

      await waitFor(() =>
        expect(screen.getByText(LABELS.emptyScreen)).toBeInTheDocument()
      )
    })

    it('should not display a venue selector, nor the mandatory input helper if there is only one venue', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue({
        venues: [MOCK_DATA.venues[0]],
      })
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      // This is a check to avoid a false positive by testing existence
      // of element to prove conjoined non-existence of another.
      await waitFor(() => {
        expect(
          screen.getAllByRole('button', {
            name: /Afficher les revenus de l'année/,
          }).length
        ).toBeGreaterThan(0)
      })

      expect(
        screen.queryByRole('button', {
          name: LABELS.secondVenueSelector,
        })
      ).not.toBeInTheDocument()

      expect(screen.queryByText(LABELS.mandatoryHelper)).not.toBeInTheDocument()
    })

    it('should display a set of year filters with the last year selected by default', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      const years = [...Object.keys(MOCK_DATA.incomeByYear)]
      await waitFor(() => {
        expect(
          screen.getAllByRole('button', {
            name: /Afficher les revenus de l'année/,
          }).length
        ).toBe(years.length)
      })

      // Years are sorted in descending order, so the last/most recent year
      // is the first item of the list of filters.
      const mostRecentYear = years.sort(
        (a, b) => parseInt(b, 10) - parseInt(a, 10)
      )[0]
      expect(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année ${mostRecentYear}`,
        })
      ).toHaveAttribute('aria-current', 'true')
    })

    it('should auto-focus the last year filter if there is only one venue', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue({
        venues: [MOCK_DATA.venues[0]],
      })
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() => {
        expect(
          screen.getAllByRole('button', {
            name: /Afficher les revenus de l'année/,
          }).length
        ).toBeGreaterThan(0)
      })

      const years = [...Object.keys(MOCK_DATA.incomeByYear)]
      // Years are sorted in descending order, so the last/most recent year
      // is the first item of the list of filters.
      const mostRecentYear = years.sort(
        (a, b) => parseInt(b, 10) - parseInt(a, 10)
      )[0]
      expect(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année ${mostRecentYear}`,
        })
      ).toHaveFocus()
    })

    it('should display the income results', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() =>
        expect(
          screen.getAllByText(LABELS.incomeResultsLabel).length
        ).toBeGreaterThan(0)
      )
    })
  })

  describe('when the user changes venue selection', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: vi.fn(),
      }))
    })

    it('should display an error if no venues are selected and avoid fetching income data', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })

      renderIncome()

      await waitFor(() => {
        expect(
          screen.getByRole('button', {
            name: LABELS.secondVenueSelector,
          })
        ).toBeInTheDocument()
      })

      const deleteVenueButtons = screen.getAllByRole('button', {
        name: /Supprimer/,
      })

      for (const button of deleteVenueButtons) {
        await userEvent.click(button)
      }

      await waitFor(
        () =>
          expect(
            screen.getByText(LABELS.venuesSelectorError)
          ).toBeInTheDocument(),
        {
          timeout: 3000,
        }
      )

      // It should not attempt to fetch income data if no venues are selected.
      expect(api.getStatistics).toHaveBeenCalledTimes(1)
    })

    it('should attempt to fetch income data with the selected venues and display a loading spinner meanwhile', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })

      renderIncome()

      await waitFor(() => {
        expect(
          screen.getByRole('button', {
            name: LABELS.secondVenueSelector,
          })
        ).toBeInTheDocument()
      })

      const deleteVenueButtons = screen.getAllByRole('button', {
        name: /Supprimer/,
      })
      const unselectedVenue = deleteVenueButtons[0]
      await userEvent.click(unselectedVenue)

      await waitFor(() =>
        expect(screen.getByTestId('income-spinner')).toBeInTheDocument()
      )
      expect(api.getStatistics).toHaveBeenNthCalledWith(2, [2])
    })
  })

  describe('when the user changes year selection', () => {
    beforeEach(() => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: vi.fn(),
      }))
    })

    it('should display the income results for the selected year', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()
      const toLocalEur = (number: number): string =>
        number.toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })

      await waitFor(() => screen.getAllByText(LABELS.incomeResultsLabel))
      const yearsWithData = Object.keys(MOCK_DATA.incomeByYear).filter(
        (year) => Object.keys(MOCK_DATA.incomeByYear[year]).length > 0
      )

      for (const y of yearsWithData) {
        await userEvent.click(
          screen.getByRole('button', {
            name: `Afficher les revenus de l'année ${y}`,
          })
        )

        const income = MOCK_DATA.incomeByYear[y]
        const incomeTypes = Object.keys(
          income
        ) as (keyof AggregatedRevenueModel)[]
        for (const t of incomeTypes) {
          const incomeResults = income[t]
          if (incomeResults) {
            if (isCollectiveAndIndividualRevenue(incomeResults)) {
              await waitFor(() =>
                expect(
                  screen.getByText(toLocalEur(incomeResults.total), {
                    collapseWhitespace: false,
                  })
                ).toBeInTheDocument()
              )
              expect(
                screen.getByText(toLocalEur(incomeResults.individual), {
                  collapseWhitespace: false,
                })
              ).toBeInTheDocument()
              expect(
                screen.getByText(toLocalEur(incomeResults.collective), {
                  collapseWhitespace: false,
                })
              ).toBeInTheDocument()
            } else if (isCollectiveRevenue(incomeResults)) {
              await waitFor(() =>
                expect(
                  screen.getByText(toLocalEur(incomeResults.collective), {
                    collapseWhitespace: false,
                  })
                ).toBeInTheDocument()
              )
            } else {
              await waitFor(() =>
                expect(
                  screen.getByText(toLocalEur(incomeResults.individual), {
                    collapseWhitespace: false,
                  })
                ).toBeInTheDocument()
              )
            }
          }
        }
      }
    })

    it('should display en empty screen if no data is available for the selected year', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })
      renderIncome()

      await waitFor(() => screen.getAllByText(LABELS.incomeResultsLabel))

      const emptyYear = Object.keys(MOCK_DATA.incomeByYear).find(
        (year) =>
          MOCK_DATA.incomeByYear[year].revenue === null &&
          MOCK_DATA.incomeByYear[year].expectedRevenue === null
      )
      await userEvent.click(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année ${emptyYear}`,
        })
      )

      await waitFor(() =>
        expect(screen.getByText(LABELS.emptyScreen)).toBeInTheDocument()
      )
    })

    it('should display previsionnal income only for current year', async () => {
      vi.spyOn(api, 'getVenues').mockResolvedValue(MOCK_DATA)
      vi.spyOn(api, 'getStatistics').mockResolvedValue({
        incomeByYear: MOCK_DATA.incomeByYear,
      })

      renderIncome()

      await waitFor(() => screen.getAllByText(LABELS.incomeResultsLabel))

      await userEvent.click(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année 1997`,
        })
      )

      expect(
        screen.getByText(LABELS.forecastIncomeResultLabel)
      ).toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', {
          name: `Afficher les revenus de l'année 1996`,
        })
      )

      expect(
        screen.queryByText(LABELS.forecastIncomeResultLabel)
      ).not.toBeInTheDocument()
    })

    it('should display total in CFP when isCaledonian is true (individual)', () => {
      vi.spyOn(useIsCaledonian, 'useIsCaledonian').mockReturnValue(true)
      vi.spyOn(
        convertEuroToPacificFranc,
        'convertEuroToPacificFranc'
      ).mockImplementation(() => 1234)
      renderWithProviders(
        <IncomeResultsBox
          type="revenue"
          income={{ individual: 100, collective: 0, total: 100 }}
        />
      )
      expect(screen.getByText('1 234 F')).toBeInTheDocument()
    })
  })
})
