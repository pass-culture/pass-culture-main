import { StatisticsModel } from "apiClient/v1";

export const statisticsFactory = ({
  emptyYear = '',
  individualRevenueOnlyYear = '',
  collectiveRevenueOnlyYear = '',
  collectiveAndIndividualRevenueYear = '2024',
}): StatisticsModel => {
  const incomeByYear = {
    ...(emptyYear && {[emptyYear]: {}}),
    ...(individualRevenueOnlyYear && {
      [individualRevenueOnlyYear]: {
        revenue: {
          individual: 1000,
        },
        expectedRevenue: {
          individual: 2000,
        }
      }
    }),
    ...(collectiveRevenueOnlyYear && {
      [collectiveRevenueOnlyYear]: {
        revenue: {
          collective: 3000,
        },
        expectedRevenue: {
          collective: 4000,
        },
      }
    }),
    [collectiveAndIndividualRevenueYear]: {
      revenue: {
        total: 11_000,
        individual: 5000,
        collective: 6000,
      },
      expectedRevenue: {
        total: 15_000,
        individual: 7000,
        collective: 8000,
      },
    },
  }

  return { incomeByYear }
}