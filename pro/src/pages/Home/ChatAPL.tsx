import { useState } from 'react'

import { UserRole } from 'apiClient/v1/models/UserRole'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Audience } from 'core/shared/types'
import styles from 'pages/Home/ChatAPL.module.css'
import OffersTableBody from 'pages/Offers/Offers/OffersTableBody/OffersTableBody'
import OffersTableHead from 'pages/Offers/Offers/OffersTableHead/OffersTableHead'
import { Button } from 'ui-kit'
import { BaseInput } from 'ui-kit/form/shared'
import { offererFactory } from 'utils/apiFactories'

const ChatAPL = (): JSX.Element => {
  const [offers, setOffers] = useState<any[]>([])
  const travelOffers = [
    51530618, 53002554, 6414992, 86412683, 6624234, 7940389, 78857402, 66423880,
    5922317, 53002426, 1513836, 1513833, 1513831, 1513829,
  ]

  function fetchOffers() {
    const offers_list: any[] = []
    travelOffers.forEach((offerId) => {
      getOffer(offerId)
        .then((offer) => {
          console.log('Successfullly fetched offer ' + offerId)
          offers_list.push(offer)
          setOffers([...offers_list])
        })
        .catch((error) => {
          console.log(error)
        })
    })
  }

  async function getOffer(offerId: number): Promise<any> {
    const response = await fetch(
      'http://localhost:5001/offers/' + offerId + '/proxy'
    )
    if (!response.ok) {
      throw new Error('Failed to fetch')
    }
    const offer = await response.json()
    return offer
  }

  const props = {
    applyFilters: () => {},
    applyUrlFiltersAndRedirect: () => {},
    areAllOffersSelected: false,
    audience: Audience.INDIVIDUAL,
    currentPageNumber: 1,
    currentPageOffersSubset: offers,
    isLoading: false,
    currentUser: {
      isAdmin: false,
      roles: [UserRole.PRO],
    },
    loadAndUpdateOffers: () => {},
    offerer: offererFactory(),
    hasOffers: false,
    setIsLoading: () => {},
    setOfferer: () => {},
    urlSearchFilters: DEFAULT_SEARCH_FILTERS,
    separateIndividualAndCollectiveOffers: false,
    initialSearchFilters: DEFAULT_SEARCH_FILTERS,
    redirectWithUrlFilters: () => {},
    venues: [],
    pageCount: 1,
    offersCount: 5,
    resetFilters: () => {},
    searchFilters: DEFAULT_SEARCH_FILTERS,
    selectedOfferIds: [],
    setSearchFilters: () => {},
    setSelectedOfferIds: () => {},
    toggleSelectAllCheckboxes: () => {},
    refreshOffers: () => {},
    isAtLeastOneOfferChecked: false,
  }

  return (
    <>
      <div>
        <BaseInput
          type="text"
          name="Prompt de génération de playlist"
          placeholder="Génère-moi une playlist de fou"
        />
        <Button
          onClick={() => {
            fetchOffers()
          }}
          className={styles['generate-button']}
        >
          Générer
        </Button>
      </div>
      <div aria-busy={false} aria-live="polite" className="section">
        <>
          {offers.length > 0 && (
            <>
              <table>
                <OffersTableHead
                  applyFilters={() => {}}
                  areAllOffersSelected={false}
                  areOffersPresent={true}
                  isAdminForbidden={() => false}
                  selectAllOffers={() => {}}
                  updateStatusFilter={() => {}}
                  audience={props.audience}
                  isAtLeastOneOfferChecked={false}
                />
                <OffersTableBody
                  areAllOffersSelected={false}
                  offers={offers}
                  selectOffer={() => {}}
                  selectedOfferIds={props.selectedOfferIds}
                  audience={props.audience}
                  refreshOffers={() => {}}
                />
              </table>
            </>
          )}
        </>
      </div>
    </>
  )
}

export default ChatAPL
