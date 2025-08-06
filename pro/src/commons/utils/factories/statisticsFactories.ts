import { StatisticsModel } from '@/apiClient/v1'

export const statisticsFactory = ({
  emptyYear = '',
  individualRevenueOnlyYear = '',
  collectiveRevenueOnlyYear = '',
  collectiveAndIndividualRevenueYear = '',
  lastYear = '',
}): StatisticsModel => {
  const incomeByYear = {
    ...(emptyYear && {
      [emptyYear]: {
        revenue: null,
        expectedRevenue: null,
      },
    }),
    ...(individualRevenueOnlyYear && {
      [individualRevenueOnlyYear]: {
        revenue: {
          individual: 1000,
        },
        ...(lastYear === individualRevenueOnlyYear && {
          expectedRevenue: {
            individual: 2000,
          },
        }),
      },
    }),
    ...(collectiveRevenueOnlyYear && {
      [collectiveRevenueOnlyYear]: {
        revenue: {
          collective: 3000,
        },
        ...(lastYear === collectiveRevenueOnlyYear && {
          expectedRevenue: {
            collective: 4000,
          },
        }),
      },
    }),
    [collectiveAndIndividualRevenueYear]: {
      revenue: {
        total: 11_430.23,
        individual: 510.23,
        collective: 10_920,
      },
      ...(lastYear === collectiveAndIndividualRevenueYear && {
        expectedRevenue: {
          total: 18_389.2,
          individual: 7_832.1,
          collective: 10_557.1,
        },
      }),
    },
  }
  return { incomeByYear }
}
