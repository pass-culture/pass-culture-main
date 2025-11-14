import {
  type CollectiveOffer,
  isCollectiveOfferBookable,
} from '@/commons/core/OfferEducational/types'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import type { Column } from '@/ui-kit/Table/Table'

import { OfferActionsCell } from './OfferActionsCell/OfferActionsCell'
import { OfferDateCell } from './OfferDateCell/OfferDateCell'
import { OfferInstitutionCell } from './OfferInstitutionCell/OfferInstitutionCell'
import { OfferLocationCell } from './OfferLocationCell/OfferLocationCell'
import { OfferNameCell } from './OfferNameCell/OfferNameCell'
import { OfferStatusCell } from './OfferStatusCell/OfferStatusCell'
import { PriceAndParticipantsCell } from './PriceAndParticipantsCell/PriceAndParticipantsCell'

export function getCollectiveOfferColumns(
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>,
  isBookableTable?: boolean
): Column<CollectiveOffer>[] {
  const columns: Column<CollectiveOffer>[] = [
    {
      id: 'name',
      label: "Nom de l'offre",
      render: (offer: CollectiveOffer) => <OfferNameCell offer={offer} />,
    },
    {
      id: 'dates',
      label: 'Dates',
      sortable: true,
      ordererField: (offer: CollectiveOffer) => offer.dates?.start || '',
      render: (offer: CollectiveOffer) => <OfferDateCell offer={offer} />,
    },
    ...(isBookableTable
      ? [
          {
            id: 'priceAndParticipants',
            label: 'Prix et participants',
            render: (offer: CollectiveOffer) =>
              isCollectiveOfferBookable(offer) && (
                <PriceAndParticipantsCell offer={offer} />
              ),
          },
          {
            id: 'institution',
            label: 'Établissement',
            render: (offer: CollectiveOffer) =>
              isCollectiveOfferBookable(offer) && (
                <OfferInstitutionCell
                  educationalInstitution={offer.educationalInstitution}
                />
              ),
          },
        ]
      : []),
    {
      id: 'location',
      label: 'Localisation',
      render: (offer: CollectiveOffer) => (
        <OfferLocationCell offerLocation={offer.location} />
      ),
    },
    {
      id: 'status',
      label: 'Statut',
      render: (offer: CollectiveOffer) => <OfferStatusCell offer={offer} />,
    },
    {
      id: 'actions',
      label: 'Actions',
      render: (offer: CollectiveOffer) => (
        <OfferActionsCell offer={offer} urlSearchFilters={urlSearchFilters} />
      ),
    },
  ]
  return columns
}
