import { StatisticsModel } from "apiClient/v1";

export const statisticsFactory = ({
  emptyYear = '',
  individualRevenueOnlyYear = '',
  collectiveRevenueOnlyYear = '',
  collectiveAndIndividualRevenueYear = '2024',
}): StatisticsModel => {
  const incomeByYear = {
    ...(emptyYear && {[emptyYear]: {
      revenue: null,
      expectedRevenue: null,
    }}),
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
        total: 11_430.23,
        individual: 510.23,
        collective: 10_920,
      },
      expectedRevenue: {
        total: 18_389.20,
        individual: 7_832.10,
        collective: 10_557.10,
      },
    },
  }

  return { incomeByYear }
}