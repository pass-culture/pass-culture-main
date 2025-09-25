import type { JSX } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import { formatAndOrderAddresses } from 'repository/venuesService'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GetOffererAddressesWithOffersOption } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import {
  GET_CATEGORIES_QUERY_KEY,
  GET_OFFERS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import {
  DEFAULT_PAGE,
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { useQuerySearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { SearchFiltersParams } from '@/commons/core/Offers/types'
import { computeIndividualOffersUrl } from '@/commons/core/Offers/utils/computeIndividualOffersUrl'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { serializeApiFilters } from '@/commons/core/Offers/utils/serializer'
import type { Audience } from '@/commons/core/shared/types'
import { useOffererAddresses } from '@/commons/hooks/swr/useOffererAddresses'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { sortByLabel } from '@/commons/utils/strings'
import { HighlightBanner } from '@/components/HighlightBanner/HighlightBanner'
import { getStoredFilterConfig } from '@/components/OffersTable/OffersTableSearch/utils'
import fullNextIcon from '@/icons/full-next.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'

import videoBannerPng from './assets/video-banner-illustration.png'
import styles from './IndividualOffers.module.scss'
import { IndividualOffersContainer } from './IndividualOffersContainer/IndividualOffersContainer'
import { computeIndividualApiFilters } from './utils/computeIndividualApiFilters'

export const IndividualOffers = (): JSX.Element => {
  const isVideoFeatureEnabled = useActiveFeature('WIP_ADD_VIDEO')
  const isNewOfferCreationFlowFFEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_OFFER_CREATION_FLOW'
  )
  const urlSearchFilters = useQuerySearchFilters()
  const { storedFilters } = getStoredFilterConfig('individual')
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(storedFilters as Partial<SearchFiltersParams>),
  }

  const currentPageNumber = finalSearchFilters.page ?? DEFAULT_PAGE
  const navigate = useNavigate()
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const categoriesQuery = useSWR(
    [GET_CATEGORIES_QUERY_KEY],
    () => api.getCategories(),
    { fallbackData: { categories: [], subcategories: [] } }
  )

  const categoriesOptions = sortByLabel(
    categoriesQuery.data.categories
      .filter((category) => category.isSelectable)
      .map((category) => ({
        value: category.id,
        label: category.proLabel,
      }))
  )

  const redirectWithSelectedFilters = (
    filters: Partial<SearchFiltersParams> & { audience?: Audience }
  ) => {
    // We dont need to pass the offererId in the URL since
    // its already present in the redux store (useSelector(selectCurrentOfferer))
    delete filters.offererId

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    navigate(computeIndividualOffersUrl(filters), { replace: true })
  }

  const offererAddressQuery = useOffererAddresses(
    GetOffererAddressesWithOffersOption.INDIVIDUAL_OFFERS_ONLY
  )
  // TODO (igabriele, 2025-07-21): offererAddresses should be unique (which is not guaranteed in current code).
  const offererAddresses = formatAndOrderAddresses(offererAddressQuery.data)

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedOffererId?.toString()
  )

  const offersQuery = useSWR([GET_OFFERS_QUERY_KEY, apiFilters], () => {
    const {
      nameOrIsbn,
      offererId,
      venueId,
      categoryId,
      status,
      creationMode,
      periodBeginningDate,
      periodEndingDate,
      offererAddressId,
      collectiveOfferType,
    } = serializeApiFilters(apiFilters)

    return api.listOffers(
      nameOrIsbn,
      offererId,
      status,
      venueId,
      categoryId,
      creationMode,
      periodBeginningDate,
      periodEndingDate,
      collectiveOfferType,
      offererAddressId
    )
  })

  const offers = offersQuery.error ? [] : offersQuery.data || []
  // This is for tracking purposes, check useLogNavigation for more details.
  const bannerVideoQueryParam = '?from_banner=banner_video'

  return (
    <HeadlineOfferContextProvider>
      <BasicLayout
        mainHeading="Offres individuelles"
        {...(isVideoFeatureEnabled
          ? {
              mainTopElement: (
                <HighlightBanner
                  title="✨ Nouveau : Ajoutez une vidéo pour donner vie à votre offre !"
                  description="2 jeunes sur 3 aimeraient voir des vidéos sur les offres culturelles du pass Culture."
                  localStorageKey="GTM_VIDEO_BANNER_2025"
                  img={
                    <img
                      className={styles['banner-img']}
                      alt=""
                      src={videoBannerPng}
                    />
                  }
                  cta={
                    <ButtonLink
                      className={styles['banner-cta']}
                      icon={fullNextIcon}
                      to={
                        isNewOfferCreationFlowFFEnabled
                          ? getIndividualOfferUrl({
                              step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
                              mode: OFFER_WIZARD_MODE.CREATION,
                              isOnboarding: false,
                            }) + bannerVideoQueryParam
                          : `/offre/creation${bannerVideoQueryParam}`
                      }
                    >
                      Créer une offre
                    </ButtonLink>
                  }
                />
              ),
            }
          : {})}
      >
        <IndividualOffersContainer
          categories={categoriesOptions}
          currentPageNumber={currentPageNumber}
          initialSearchFilters={apiFilters}
          isLoading={offersQuery.isLoading}
          offers={offers}
          redirectWithSelectedFilters={redirectWithSelectedFilters}
          offererAddresses={offererAddresses}
        />
      </BasicLayout>
    </HeadlineOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOffers
