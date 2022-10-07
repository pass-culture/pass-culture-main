import {
  CollectiveOfferFromTemplateResponseModel,
  CollectiveStockResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  CollectiveOffer,
  CollectiveOfferTemplate,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

export const extractInitialStockValues = (
  stock:
    | CollectiveOfferFromTemplateResponseModel
    | GetCollectiveOfferTemplateResponseModel
    | CollectiveStockResponseModel
    | null,
  offer: CollectiveOffer | CollectiveOfferTemplate,
  offerType: EducationalOfferType
): OfferEducationalStockFormValues => {
  if (!stock) {
    return DEFAULT_EAC_STOCK_FORM_VALUES
  }

  if (offerType === EducationalOfferType.CLASSIC) {
    const typedStock = stock as CollectiveOfferFromTemplateResponseModel
    return {
      eventDate:
        getLocalDepartementDateTimeFromUtc(
          typedStock.beginningDatetime,
          offer.venue.departementCode
        ) ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventDate,
      eventTime:
        getLocalDepartementDateTimeFromUtc(
          typedStock.beginningDatetime,
          offer.venue.departementCode
        ) ?? DEFAULT_EAC_STOCK_FORM_VALUES.eventTime,
      numberOfPlaces:
        typedStock.numberOfTickets ??
        DEFAULT_EAC_STOCK_FORM_VALUES.numberOfPlaces,
      totalPrice: typedStock.price,
      bookingLimitDatetime:
        getLocalDepartementDateTimeFromUtc(typedStock.bookingLimitDatetime) ??
        DEFAULT_EAC_STOCK_FORM_VALUES.bookingLimitDatetime,
      priceDetail:
        typedStock.educationalPriceDetail ??
        DEFAULT_EAC_STOCK_FORM_VALUES.priceDetail,
      educationalOfferType: offer.isTemplate
        ? EducationalOfferType.SHOWCASE
        : EducationalOfferType.CLASSIC,
    }
  }

  return {
    ...DEFAULT_EAC_STOCK_FORM_VALUES,
    priceDetail:
      stock.educationalPriceDetail ?? DEFAULT_EAC_STOCK_FORM_VALUES.priceDetail,
    educationalOfferType: offer.isTemplate
      ? EducationalOfferType.SHOWCASE
      : EducationalOfferType.CLASSIC,
  }
}
