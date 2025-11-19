import { IndividualOfferLocation } from '../IndividualOfferLocation/IndividualOfferLocation'

// TODO (igabriele, 2025-08-14): Replace this page with `<IndividualOfferLocation />` once `WIP_ENABLE_NEW_OFFER_CREATION_FLOW` FF is enabled in production.
const IndividualOfferInformations = (): JSX.Element | null => {
  // Getting selected venue at step 1 (details) to infer address fields

  return <IndividualOfferLocation />
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferInformations
