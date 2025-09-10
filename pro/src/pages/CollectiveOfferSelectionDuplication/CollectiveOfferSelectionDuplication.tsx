import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferType,
} from '@/apiClient/v1'
import { Layout } from '@/app/App/layout/Layout'
import { GET_COLLECTIVE_OFFERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { createOfferFromTemplate } from '@/commons/core/OfferEducational/utils/createOfferFromTemplate'
import { DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializer'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useNotification } from '@/commons/hooks/useNotification'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { pluralize } from '@/commons/utils/pluralize'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { TextInput } from '@/design-system/TextInput/TextInput'
import strokeSearchIcon from '@/icons/stroke-search.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Spinner } from '@/ui-kit/Spinner/Spinner'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { CardLink } from '../../ui-kit/CardLink/CardLink'
import styles from './CollectiveOfferSelectionDuplication.module.scss'
import { SkeletonLoader } from './CollectiveOfferSelectionLoaderSkeleton'

export const CollectiveOfferSelectionDuplication = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()

  const isMarseilleActive = useActiveFeature('ENABLE_MARSEILLE')
  const isCollectiveOaActive = useActiveFeature(
    'WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE'
  )
  const [searchedOfferName, setSearchedOfferName] = useState('')
  const [typedOfferName, setTypedOfferName] = useState('')
  const [isCreatingNewOffer, setIsCreatingNewOffer] = useState(false)

  const queryParams = new URLSearchParams(location.search)
  const currentOffererId = useSelector(selectCurrentOffererId)
  const queryVenueId = queryParams.get('lieu')

  const {
    nameOrIsbn,
    offererId,
    venueId,
    status,
    creationMode,
    periodBeginningDate,
    periodEndingDate,
    format,
  } = serializeApiCollectiveFilters(
    {
      ...DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
      nameOrIsbn: searchedOfferName,
      offererId: currentOffererId ? currentOffererId.toString() : 'all',
      venueId: queryVenueId ? queryVenueId : 'all',
      status: [
        CollectiveOfferDisplayedStatus.PUBLISHED,
        CollectiveOfferDisplayedStatus.HIDDEN,
        CollectiveOfferDisplayedStatus.ENDED,
      ],
    },
    DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS
  )

  const { data: offers, isLoading } = useSWR(
    [GET_COLLECTIVE_OFFERS_QUERY_KEY, nameOrIsbn],
    () =>
      api.getCollectiveOffers(
        nameOrIsbn,
        offererId,
        status,
        venueId,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        CollectiveOfferType.TEMPLATE,
        format
      ),
    {
      onError: (e) => {
        notify.error(GET_DATA_ERROR_MESSAGE)
      },
    }
  )

  const navigateToOffer = async (offerId: number) => {
    setIsCreatingNewOffer(true)

    try {
      await createOfferFromTemplate(
        navigate,
        notify,
        offerId,
        isCollectiveOaActive,
        undefined,
        isMarseilleActive,
        setIsCreatingNewOffer
      )
    } catch {
      setIsCreatingNewOffer(false)
      notify.error(GET_DATA_ERROR_MESSAGE)
    }
  }

  if (isCreatingNewOffer) {
    return (
      <Layout
        layout={'sticky-actions'}
        mainHeading="Créer une offre réservable"
      >
        <div className="container">
          <Spinner message="Création de la nouvelle offre réservable en cours" />
        </div>
      </Layout>
    )
  }

  return (
    <Layout layout={'sticky-actions'} mainHeading="Créer une offre réservable">
      <div className="container">
        <div className={styles['search-container']}>
          <form
            className={styles['search-input-container']}
            aria-labelledby="search-filter"
            onSubmit={(e) => {
              setSearchedOfferName(typedOfferName)
              e.stopPropagation()
              e.preventDefault()
            }}
          >
            <div className={styles['search-input']}>
              <TextInput
                label="Rechercher l’offre vitrine à dupliquer"
                value={typedOfferName}
                name="searchFilter"
                type="search"
                autoComplete="off"
                icon={strokeSearchIcon}
                onChange={(e) => {
                  setTypedOfferName(e.target.value)
                }}
                extension={
                  <Button
                    type="submit"
                    className={styles['search-button']}
                    disabled={isLoading}
                  >
                    Rechercher
                  </Button>
                }
              />
            </div>
          </form>

          {isLoading ? (
            <SkeletonLoader />
          ) : (
            <>
              {/** biome-ignore lint/a11y/useSemanticElements: What we want here is a role status */}
              <p className={styles['visually-hidden']} role="status">
                {offers && pluralize(offers.length, 'offre vitrine trouvée')}
              </p>
              <p className={styles['legend']}>
                {searchedOfferName.length < 1
                  ? 'Les dernières offres vitrines créées'
                  : `${offers && pluralize(offers.length, 'offre')}` +
                    ' vitrine'}
              </p>
              <ul className={styles['list']}>
                {(offers || []).slice(0, 5).map((offer) => (
                  <li key={offer.id}>
                    <CardLink
                      label={offer.name}
                      description={offer.venue.name}
                      onClick={() => {
                        navigateToOffer(offer.id)
                      }}
                    />
                  </li>
                ))}
              </ul>

              {offers && offers.length < 1 && (
                <div className={styles['search-no-results']}>
                  <SvgIcon
                    src={strokeSearchIcon}
                    alt="Illustration de recherche"
                    className={styles['search-no-results-icon']}
                    width="124"
                  />
                  <p className={styles['search-no-results-text']}>
                    Aucune offre trouvée pour votre recherche
                  </p>
                </div>
              )}

              <ActionsBarSticky>
                <ActionsBarSticky.Left>
                  <ButtonLink
                    variant={ButtonVariant.SECONDARY}
                    to={computeCollectiveOffersUrl({})}
                  >
                    Retour à la liste des offres
                  </ButtonLink>
                </ActionsBarSticky.Left>
              </ActionsBarSticky>
            </>
          )}
        </div>
      </div>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveOfferSelectionDuplication
