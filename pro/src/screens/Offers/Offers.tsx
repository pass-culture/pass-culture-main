import { useState } from 'react'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferResponseModel,
  GetOffererResponseModel,
  ListOffersOfferResponseModel,
  OfferStatus,
  UserRole,
} from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { NoData } from 'components/NoData/NoData'
import { GET_VALIDATED_OFFERERS_NAMES_QUERY_KEY } from 'config/swrQueryKeys'
import { isOfferEducational } from 'core/OfferEducational/types'
import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
  MAX_TOTAL_PAGES,
  NUMBER_OF_OFFERS_PER_PAGE,
  OFFER_STATUS_DRAFT,
} from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import {
  computeOffersUrl,
  computeCollectiveOffersUrl,
} from 'core/Offers/utils/computeOffersUrl'
import { hasSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { Audience } from 'core/shared/types'
import { SelectOption } from 'custom_types/form'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import fullPlusIcon from 'icons/full-plus.svg'
import strokeLibraryIcon from 'icons/stroke-library.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { Offers as OffersContainer } from 'pages/Offers/Offers/Offers'
import { CollectiveOffersActionsBar } from 'pages/Offers/Offers/OffersActionsBar/CollectiveOffersActionsBar'
import { IndividualOffersActionsBar } from 'pages/Offers/Offers/OffersActionsBar/IndividualOffersActionsBar'
import { isSameOffer } from 'pages/Offers/utils/isSameOffer'
import { selectCurrentOffererId } from 'store/user/selectors'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Tabs } from 'ui-kit/Tabs/Tabs'
import { Titles } from 'ui-kit/Titles/Titles'

import styles from './Offers.module.scss'
import { SearchFilters } from './SearchFilters/SearchFilters'

export type OffersProps = {
  currentPageNumber: number
  currentUser: {
    roles: Array<UserRole>
    isAdmin: boolean
  }
  isLoading: boolean
  offerer: GetOffererResponseModel | null
  initialSearchFilters: SearchFiltersParams
  redirectWithUrlFilters: (
    filters: SearchFiltersParams & {
      page?: number
      audience?: Audience
    }
  ) => void
  urlSearchFilters: SearchFiltersParams
  venues: SelectOption[]
  categories?: SelectOption[]
  isRestrictedAsAdmin?: boolean
} & (
  | { audience: Audience.COLLECTIVE; offers: CollectiveOfferResponseModel[] }
  | { audience: Audience.INDIVIDUAL; offers: ListOffersOfferResponseModel[] }
)

export const Offers = ({
  currentPageNumber,
  currentUser,
  isLoading,
  offerer,
  initialSearchFilters,
  audience,
  redirectWithUrlFilters,
  urlSearchFilters,
  venues,
  categories,
  isRestrictedAsAdmin,
  offers,
}: OffersProps): JSX.Element => {
  const [selectedCollectiveOffers, setSelectedCollectiveOffers] = useState<
    CollectiveOfferResponseModel[]
  >([])
  const [selectedIndividualOffers, setSelectedIndividualOffers] = useState<
    ListOffersOfferResponseModel[]
  >([])
  const isNewSideBarNavigation = useIsNewInterfaceActive()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const [selectedFilters, setSelectedFilters] = useState(initialSearchFilters)

  const isCollective = audience === Audience.COLLECTIVE

  const { isAdmin } = currentUser
  const currentPageOffersSubset = offers.slice(
    (currentPageNumber - 1) * NUMBER_OF_OFFERS_PER_PAGE,
    currentPageNumber * NUMBER_OF_OFFERS_PER_PAGE
  )
  const hasOffers = currentPageOffersSubset.length > 0

  const userHasNoOffers =
    !isLoading && !hasOffers && !hasSearchFilters(urlSearchFilters)

  const validatedUserOfferersQuery = useSWR(
    !isAdmin ? [GET_VALIDATED_OFFERERS_NAMES_QUERY_KEY] : null,
    () => api.listOfferersNames(undefined, true)
  )

  const isOffererValidated =
    validatedUserOfferersQuery.data?.offerersNames.some(
      (validatedOfferer) => validatedOfferer.id === selectedOffererId
    )
  const displayCreateOfferButton =
    !isNewSideBarNavigation && !isAdmin && isOffererValidated

  const actionLink = displayCreateOfferButton ? (
    <ButtonLink
      variant={ButtonVariant.PRIMARY}
      to={`/offre/creation${selectedOffererId ? `?structure=${selectedOffererId}` : ''}`}
      icon={fullPlusIcon}
    >
      Créer une offre
    </ButtonLink>
  ) : undefined

  const areAllCollectiveOffersSelected =
    selectedCollectiveOffers.length > 0 &&
    selectedCollectiveOffers.length ===
      offers.filter((offer) => offer.isEditable).length

  const areAllIndividualOffersSelected =
    selectedIndividualOffers.length > 0 &&
    selectedIndividualOffers.length === offers.length

  function clearSelectedOfferIds() {
    setSelectedCollectiveOffers([])
    setSelectedIndividualOffers([])
  }

  function toggleSelectAllCheckboxes() {
    if (isCollective) {
      setSelectedCollectiveOffers(
        areAllCollectiveOffersSelected
          ? []
          : offers.filter((offer) => offer.isEditable)
      )
    } else {
      setSelectedIndividualOffers(areAllIndividualOffersSelected ? [] : offers)
    }
  }

  const resetFilters = () => {
    setSelectedFilters(DEFAULT_SEARCH_FILTERS)
    applyUrlFiltersAndRedirect({
      ...DEFAULT_SEARCH_FILTERS,
    })
  }

  const numberOfPages = Math.ceil(offers.length / NUMBER_OF_OFFERS_PER_PAGE)
  const pageCount = Math.min(numberOfPages, MAX_TOTAL_PAGES)

  const applyUrlFiltersAndRedirect = (
    filters: SearchFiltersParams & { audience?: Audience }
  ) => {
    redirectWithUrlFilters(filters)
  }

  const applyFilters = (filters: SearchFiltersParams) => {
    applyUrlFiltersAndRedirect({ ...filters, page: DEFAULT_PAGE })
  }

  const removeOfferer = () => {
    const updatedFilters = {
      ...initialSearchFilters,
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
    }
    if (
      initialSearchFilters.venueId === DEFAULT_SEARCH_FILTERS.venueId &&
      initialSearchFilters.status !== DEFAULT_SEARCH_FILTERS.status
    ) {
      updatedFilters.status = DEFAULT_SEARCH_FILTERS.status
    }
    applyUrlFiltersAndRedirect(updatedFilters)
  }

  const getUpdateOffersStatusMessage = (tmpSelectedOfferIds: number[]) => {
    const selectedOffers = offers.filter((offer) =>
      tmpSelectedOfferIds.includes(offer.id)
    )
    if (selectedOffers.some((offer) => offer.status === OFFER_STATUS_DRAFT)) {
      return 'Vous ne pouvez pas publier des brouillons depuis cette liste'
    }
    if (
      isCollective &&
      selectedOffers.some((offer) => offer.hasBookingLimitDatetimesPassed)
    ) {
      return 'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
    }
    return ''
  }

  const canDeleteOffers = (
    isCollective ? selectedCollectiveOffers : selectedIndividualOffers
  ).some((offer) => offer.status === OfferStatus.DRAFT)

  const isNewInterfaceActive = useIsNewInterfaceActive()
  const title = isNewInterfaceActive
    ? audience === Audience.COLLECTIVE
      ? 'Offres collectives'
      : 'Offres individuelles'
    : 'Offres'

  function onSetSelectedOffer(
    offer: ListOffersOfferResponseModel | CollectiveOfferResponseModel
  ) {
    const matchingOffer = (
      isCollective ? selectedCollectiveOffers : selectedIndividualOffers
    ).find((selectedOffer) => isSameOffer(offer, selectedOffer))

    if (isOfferEducational(offer)) {
      if (matchingOffer) {
        setSelectedCollectiveOffers((offers) =>
          offers.filter((collectiveOffer) => collectiveOffer !== matchingOffer)
        )
      } else {
        setSelectedCollectiveOffers((selectedOffers) => {
          return [...selectedOffers, offer]
        })
      }
    } else {
      if (matchingOffer) {
        setSelectedIndividualOffers((offers) =>
          offers.filter((indivOffer) => indivOffer !== matchingOffer)
        )
      } else {
        setSelectedIndividualOffers((selectedOffers) => {
          return [...selectedOffers, offer]
        })
      }
    }
  }

  return (
    <div className="offers-page">
      <Titles action={actionLink} title={title} />
      {!isNewSideBarNavigation && (
        <Tabs
          nav="Offres individuelles et collectives"
          selectedKey={audience}
          tabs={[
            {
              label: 'Offres individuelles',
              url: computeOffersUrl({
                ...initialSearchFilters,
                status: DEFAULT_SEARCH_FILTERS.status,
                page: currentPageNumber,
              }),
              key: 'individual',
              icon: strokeUserIcon,
            },
            {
              label: 'Offres collectives',
              url: computeCollectiveOffersUrl({
                ...initialSearchFilters,
                status: DEFAULT_SEARCH_FILTERS.status,
                page: currentPageNumber,
              }),
              key: 'collective',
              icon: strokeLibraryIcon,
            },
          ]}
        />
      )}

      <SearchFilters
        applyFilters={applyFilters}
        audience={audience}
        categories={categories}
        disableAllFilters={userHasNoOffers}
        offerer={offerer}
        removeOfferer={removeOfferer}
        resetFilters={resetFilters}
        selectedFilters={selectedFilters}
        setSelectedFilters={setSelectedFilters}
        venues={venues}
        isRestrictedAsAdmin={isRestrictedAsAdmin}
      />
      {Audience.COLLECTIVE === audience && (
        <Callout
          className={styles['banner']}
          variant={CalloutVariant.INFO}
          links={[
            {
              href: 'https://aide.passculture.app/hc/fr/articles/4416082284945--Acteurs-Culturels-Quel-est-le-cycle-de-vie-de-votre-offre-collective-de-sa-cr%C3%A9ation-%C3%A0-son-remboursement',
              label: 'En savoir plus sur les statuts',
              isExternal: true,
            },
          ]}
        >
          <div className={styles['banner-onboarding']}>
            <span className={styles['banner-onboarding-title']}>
              C’est nouveau ! Vous pouvez désormais archiver vos offres
              collectives.
            </span>
            <span>
              Cliquez sur le bouton “Actions” pour archiver vos offres. Elles ne
              seront plus visibles sur ADAGE. Vous pourrez les retrouver en
              filtrant sur le statut “Archivée”.{' '}
            </span>
          </div>
        </Callout>
      )}
      {userHasNoOffers ? (
        <NoData page="offers" />
      ) : (
        <OffersContainer
          applyUrlFiltersAndRedirect={applyUrlFiltersAndRedirect}
          areAllOffersSelected={
            isCollective
              ? areAllCollectiveOffersSelected
              : areAllIndividualOffersSelected
          }
          audience={audience}
          currentPageNumber={currentPageNumber}
          currentPageOffersSubset={currentPageOffersSubset}
          currentUser={currentUser}
          hasOffers={hasOffers}
          isLoading={isLoading}
          offersCount={offers.length}
          pageCount={pageCount}
          resetFilters={resetFilters}
          selectedOffers={
            isCollective ? selectedCollectiveOffers : selectedIndividualOffers
          }
          setSelectedOffer={onSetSelectedOffer}
          toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
          urlSearchFilters={urlSearchFilters}
          isAtLeastOneOfferChecked={
            isCollective
              ? selectedCollectiveOffers.length > 1
              : selectedIndividualOffers.length > 1
          }
          isRestrictedAsAdmin={isRestrictedAsAdmin}
        />
      )}
      {isCollective
        ? selectedCollectiveOffers.length > 0 && (
            <CollectiveOffersActionsBar
              areAllOffersSelected={areAllCollectiveOffersSelected}
              clearSelectedOfferIds={clearSelectedOfferIds}
              selectedOffers={selectedCollectiveOffers}
              toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
              getUpdateOffersStatusMessage={getUpdateOffersStatusMessage}
            />
          )
        : selectedIndividualOffers.length > 0 && (
            <IndividualOffersActionsBar
              areAllOffersSelected={areAllIndividualOffersSelected}
              clearSelectedOfferIds={clearSelectedOfferIds}
              selectedOfferIds={selectedIndividualOffers.map(
                (offer) => offer.id
              )}
              toggleSelectAllCheckboxes={toggleSelectAllCheckboxes}
              getUpdateOffersStatusMessage={getUpdateOffersStatusMessage}
              canDeleteOffers={canDeleteOffers}
            />
          )}
    </div>
  )
}
