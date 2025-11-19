/* istanbul ignore file */

import { IndividualOfferSummaryPriceTable } from '../IndividualOfferSummaryPriceTable/IndividualOfferSummaryPriceTable'

const IndividualOfferSummaryPriceCategories = (): JSX.Element | null => {
  return <IndividualOfferSummaryPriceTable />
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferSummaryPriceCategories
