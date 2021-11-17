import { IOfferTypeProps } from "../OfferType"

export const setDefaultProps = (): IOfferTypeProps => ({
  fetchCanOffererCreateEducationalOffer: jest.fn().mockResolvedValue({})
})
