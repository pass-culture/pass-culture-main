import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import { format } from 'date-fns'

import type {
  GetVenueOffersStatsV2ResponseModel,
  StatisticsModel,
  TopOfferResponseModel,
  VenueMonthlyViewModel,
  VenueOffersPeriodStatsModel,
} from '@/apiClient/v1'

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

const topOfferResponseModelFactory = (
  customTopOfferResponseModel: Partial<TopOfferResponseModel> = {}
) => {
  return {
    image: null,
    isHeadlineOffer: false,
    name: 'name',
    offerId: 1,
    views: 0,
    ...customTopOfferResponseModel,
  }
}

export const venueMonthlyViewModelFactory = (
  customVenueMonthlyViewModel: Partial<VenueMonthlyViewModel> = {}
) => {
  return {
    month: format(new Date(), FORMAT_ISO_DATE_ONLY),
    views: 0,
    ...customVenueMonthlyViewModel,
  }
}

export const venueOffersPeriodStatsModelFactory = (
  customVenueOffersPeriodStatsModel: Partial<VenueOffersPeriodStatsModel> = {}
): VenueOffersPeriodStatsModel => {
  return {
    cumulatedViews: 0,
    topOffers: customVenueOffersPeriodStatsModel.topOffers?.map(
      topOfferResponseModelFactory
    ) || [topOfferResponseModelFactory()],
    viewsByMonth: customVenueOffersPeriodStatsModel.viewsByMonth?.map(
      venueMonthlyViewModelFactory
    ) || [venueMonthlyViewModelFactory()],
    ...customVenueOffersPeriodStatsModel,
  }
}

export const getVenueOffersStatsV2ResponseModelFactory = (
  customGetVenueOffersStatsV2ResponseModel: Partial<GetVenueOffersStatsV2ResponseModel> = {}
) => {
  return {
    last3Months: venueOffersPeriodStatsModelFactory(
      customGetVenueOffersStatsV2ResponseModel?.last3Months
    ),
    last6Months: venueOffersPeriodStatsModelFactory(
      customGetVenueOffersStatsV2ResponseModel?.last6Months
    ),
    venueId: 1,
    ...customGetVenueOffersStatsV2ResponseModel,
  }
}
