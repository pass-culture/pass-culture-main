import React from 'react'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
} from 'apiClient/v1'
import { computeURLCollectiveOfferId } from 'commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { OfferVenueCell } from 'components/CollectiveOffersTable/CollectiveOfferRow/OfferVenueCell/OfferVenueCell'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel/CollectiveStatusLabel'
import { Column } from 'ui-kit/ResponsiveTable/ResponsiveTable'

import { CollectiveActionsCells } from './CollectiveActionsCells/CollectiveActionsCells'
import { ExpirationCell } from './ExpirationCell/ExpirationCell'
import { OfferEventDateCell } from './OfferEventDateCell/OfferEventDateCell'
import { OfferInstitutionCell } from './OfferInstitutionCell/OfferInstitutionCell'
import { OfferNameCell } from './OfferNameCell/OfferNameCell'

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------
const isPublishedOrPreBooked = (offer: CollectiveOfferResponseModel) =>
  offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED ||
  offer.displayedStatus === CollectiveOfferDisplayedStatus.PREBOOKED

const buildLinks = (
  offer: CollectiveOfferResponseModel,
  newDetailPage: boolean,
) => {
  const id = computeURLCollectiveOfferId(offer.id, Boolean(offer.isShowcase))
  const draft =
    offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT

  const detail =
    newDetailPage && !offer.isShowcase
      ? `/offre/${id}/collectif/recapitulatif`
      : draft
        ? `/offre/collectif/${id}/creation`
        : `/offre/${id}/collectif/recapitulatif`

  const edit = draft
    ? `/offre/collectif/${id}/creation`
    : `/offre/${id}/collectif/edition`

  return { id, detail, edit }
}

// -----------------------------------------------------------------------------
// Factory
// -----------------------------------------------------------------------------
interface ColumnFactoryParams {
  /** which offers are currently selected */
  selectedIds: Set<string | number>
  /** handler used to toggle selection (receives the offer row) */
  toggleSelect: (o: CollectiveOfferResponseModel) => void
  /** URL filters to forward to the actions cell */
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>
}

export function createCollectiveOfferColumns(
  params: ColumnFactoryParams,
): {
  columns: Column<CollectiveOfferResponseModel>[]
  getExpandedContent: (
    o: CollectiveOfferResponseModel,
  ) => React.ReactNode | null
  getRowLink: string
} {
  const { selectedIds, toggleSelect, urlSearchFilters } = params
  const newDetailPageActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFER_DETAIL_PAGE',
  )

  // ---- expanded cell renderer ------------------------------------------------
  const getExpandedContent = (
    offer: CollectiveOfferResponseModel,
  ): React.ReactNode | null => {
    const bookingLimitDate = offer.stocks[0]?.bookingLimitDatetime
    if (
      !offer.isShowcase &&
      isPublishedOrPreBooked(offer) &&
      bookingLimitDate
    ) {
      const { id } = buildLinks(offer, newDetailPageActive)
      return React.createElement(ExpirationCell, {
        rowId: `collective-offer-${id}`,
        offer,
        bookingLimitDate,
      })
    }
    return null
  }

  // ---- columns ---------------------------------------------------------------
  const columns: Column<CollectiveOfferResponseModel>[] = [
    {
      id: 'offer-head-name',
      label: "Nom de l'offre",
      render: (offer) => {
        return React.createElement(OfferNameCell, {
          offer,
          displayThumb: true,
        })
      },
    },    

    // 4. Event date (sortable) --------------------------------------------------
    {
      id: 'offer-head-event-date',
      label: 'Date de l’évènement',
      sortable: true,
      accessor: (offer) => offer.dates?.start,         
      render: offer => {
        return React.createElement(OfferEventDateCell, {
          offer,
        })
      },
    },

    // 5. Venue -----------------------------------------------------------------
    {
      id: 'offer-head-structure',
      label: 'Lieu',
      render: offer =>
        React.createElement(OfferVenueCell, {
          venue: offer.venue,
        }),
    },

    // 6. Institution -----------------------------------------------------------
    {
      id: 'offer-head-institution',
      label: 'Structure',
      render: offer =>
        React.createElement(OfferInstitutionCell, {
          educationalInstitution: offer.educationalInstitution,
        }),
    },

    // 7. Status ----------------------------------------------------------------
    {
      id: 'offer-head-status',
      label: 'Statut',
      render: offer =>
        React.createElement(CollectiveStatusLabel, {
          offerDisplayedStatus: offer.displayedStatus,
        }),
    },

    // 8. Actions ---------------------------------------------------------------
    {
      id: 'offer-head-actions',
      label: 'Actions',
      render: offer => {
        const { edit } = buildLinks(offer, newDetailPageActive)
        const isSelected = selectedIds.has(offer.id)

        return React.createElement(CollectiveActionsCells, {
          offer,
          editionOfferLink: edit,
          urlSearchFilters,
          isSelected,
          deselectOffer: () => toggleSelect(offer),
        })
      },
    },
  ]

  // ---- row link builder ------------------------------------------------------
  const getRowLink = (offer: CollectiveOfferResponseModel) =>
    buildLinks(offer, newDetailPageActive).detail

  return { columns, getExpandedContent, getRowLink }
}
