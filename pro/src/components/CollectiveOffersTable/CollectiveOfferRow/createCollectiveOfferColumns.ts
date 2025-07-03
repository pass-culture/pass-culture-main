// createCollectiveOfferColumns.ts
import React from 'react'

import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
} from 'apiClient/v1'
import { computeURLCollectiveOfferId } from 'commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { isCollectiveOfferSelectable } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { OfferVenueCell } from 'components/CollectiveOffersTable/CollectiveOfferRow/OfferVenueCell'
import { ThumbCell } from 'components/CollectiveOffersTable/CollectiveOfferRow/ThumbCell'
import { Column } from 'ui-kit/ResponsiveTable/ResponsiveTable'

import { CollectiveActionsCells } from './CollectiveActionsCells/CollectiveActionsCells'
import { CollectiveOfferStatusCell } from './CollectiveOfferStatusCell/CollectiveOfferStatusCell'
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
  getRowLink: (o: CollectiveOfferResponseModel) => string
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
      id: 'offerHeader', // clé principale pour l’en-tête
      label: "Nom de l'offre",
      headerColSpan: 2, // 👈 regroupe les deux sous-colonnes
      sortable: true,
      accessor: 'name', // pour que le tri fonctionne
      bodyHidden: true, // 👈 pas de cellule dans le body
    },
    {
      id: 'offer-head-thumb',
      label: '',
      headerHidden: true, // 👈 pas de cellule dans l’en-tête
      render: (offer) => {
        const { id, detail } = buildLinks(offer, newDetailPageActive)
        const selectable = isCollectiveOfferSelectable(offer)
        return React.createElement(ThumbCell, {
          rowId: `collective-offer-${id}`,
          offer,
          offerLink: detail,
          inactive: !selectable,
        })
      },
    },
    {
      id: 'offer-head-name',
      label: '',
      headerHidden: true, // 👈 pas de cellule dans l’en-tête
      render: (offer) => {
        const { id, detail } = buildLinks(offer, newDetailPageActive)
        return React.createElement(OfferNameCell, {
          rowId: `collective-offer-${id}`,
          offer,
          offerLink: detail,
        })
      },
    },    

    // 4. Event date (sortable) --------------------------------------------------
    {
      id: 'offer-head-event-date',
      label: 'Date',
      sortable: true,
      width: '8rem',
      render: offer => {
        const { id } = buildLinks(offer, newDetailPageActive)

        return React.createElement(OfferEventDateCell, {
          rowId: `collective-offer-${id}`,
          offer,
        })
      },
    },

    // 5. Venue -----------------------------------------------------------------
    {
      id: 'offer-head-structure',
      label: 'Lieu',
      width: '14rem',
      render: offer =>
        React.createElement(OfferVenueCell, {
          rowId: `collective-offer-${offer.id}`,
          venue: offer.venue,
        }),
    },

    // 6. Institution -----------------------------------------------------------
    {
      id: 'offer-head-institution',
      label: 'Structure',
      width: '16rem',
      render: offer =>
        React.createElement(OfferInstitutionCell, {
          rowId: `collective-offer-${offer.id}`,
          educationalInstitution: offer.educationalInstitution,
        }),
    },

    // 7. Status ----------------------------------------------------------------
    {
      id: 'offer-head-status',
      label: 'Statut',
      width: '10rem',
      render: offer =>
        React.createElement(CollectiveOfferStatusCell, {
          rowId: `collective-offer-${offer.id}`,
          offer,
        }),
    },

    // 8. Actions ---------------------------------------------------------------
    {
      id: 'offer-head-actions',
      label: 'Actions',
      width: '8rem',
      render: offer => {
        const { edit } = buildLinks(offer, newDetailPageActive)
        const isSelected = selectedIds.has(offer.id)

        return React.createElement(CollectiveActionsCells, {
          rowId: `collective-offer-${offer.id}`,
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
