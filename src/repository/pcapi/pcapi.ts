import { client } from "repository/pcapi/pcapiClient"
import { OfferType } from "utils/types"

export const authenticate = async (): Promise<void> => {
  return client.get("/adage-iframe/authenticate")
}

export const getOffer = async (
  offerId: number | string
): Promise<OfferType> => {
  return client.get(`/native/v1/offer/${offerId}`)
}

export const preBookStock = async (stockId: number): Promise<number> => {
  return client.post("/adage-iframe/bookings", { stockId })
}
