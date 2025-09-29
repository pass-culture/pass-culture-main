import { computeAddressDisplayName } from 'repository/venuesService'

import type {
  HeadLineOfferResponseModel,
  ListOffersOfferResponseModel,
} from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_STATUS_DRAFT,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import type { Column } from '@/ui-kit/Table/Table'

import { IndividualActionsCells } from './components/IndividualActionsCells'
import { OfferBookingCell } from './components/OfferBookingCell/OfferBookingCell'
import { OfferNameCell } from './components/OfferNameCell/OfferNameCell'
import { OfferStatusCell } from './components/OfferStatusCell/OfferStatusCell'

export function getIndividualOfferColumns(
  headlineOffer: HeadLineOfferResponseModel | null,
  isHeadlineOfferAllowedForOfferer: boolean,
  isNewOfferCreationFlowFFEnabled: boolean
): Column<ListOffersOfferResponseModel>[] {
  const columns: Column<ListOffersOfferResponseModel>[] = [
    {
      id: 'name',
      label: 'Nom de l’offre',
      render: (offer) => {
        const offerLink = getIndividualOfferUrl({
          offerId: offer.id,
          mode:
            offer.status === OFFER_STATUS_DRAFT
              ? OFFER_WIZARD_MODE.CREATION
              : OFFER_WIZARD_MODE.READ_ONLY,
          step: isNewOfferCreationFlowFFEnabled
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
        })

        return <OfferNameCell offer={offer} offerLink={offerLink} />
      },
    },
    {
      id: 'address',
      label: 'Localisation',
      render: (offer) =>
        offer.address ? computeAddressDisplayName(offer.address) : '-',
    },
    {
      id: 'stocks',
      label: 'Stocks',
      render: (offer) => {
        let totalRemainingStock = 0

        for (const stock of offer.stocks) {
          if (stock.remainingQuantity === 'unlimited') {
            return 'Illimité'
          }
          totalRemainingStock += Number(stock.remainingQuantity)
        }
        return new Intl.NumberFormat('fr-FR').format(totalRemainingStock)
      },
    },
    {
      id: 'status',
      label: 'Publication',
      render: (offer) => (
        <OfferStatusCell
          offer={offer}
          isHeadline={
            isHeadlineOfferAllowedForOfferer && offer.id === headlineOffer?.id
          }
        />
      ),
    },
    {
      id: 'bookingsCount',
      label: 'Réservations',
      render: (offer) => <OfferBookingCell offer={offer} />,
    },
    {
      id: 'actions',
      label: 'Actions',
      render: (offer) => {
        const offerLink = getIndividualOfferUrl({
          offerId: offer.id,
          mode:
            offer.status === OFFER_STATUS_DRAFT
              ? OFFER_WIZARD_MODE.CREATION
              : OFFER_WIZARD_MODE.READ_ONLY,
          step: isNewOfferCreationFlowFFEnabled
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
        })

        const editionStockLink = getIndividualOfferUrl({
          offerId: offer.id,
          mode: OFFER_WIZARD_MODE.EDITION,
          step: isNewOfferCreationFlowFFEnabled
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
        })

        return (
          <IndividualActionsCells
            offer={offer}
            editionOfferLink={offerLink}
            editionStockLink={editionStockLink}
          />
        )
      },
    },
  ]

  return columns
}
