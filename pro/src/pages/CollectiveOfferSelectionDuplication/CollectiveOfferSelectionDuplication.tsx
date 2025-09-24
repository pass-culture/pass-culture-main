import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferType,
} from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
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

type SearchFormValues = {
  searchQuery: string
}

export const CollectiveOfferSelectionDuplication = (): JSX.Element => {
  const notify = useNotification()
  const navigate = useNavigate()

  const isMarseilleActive = useActiveFeature('ENABLE_MARSEILLE')

  const form = useForm<SearchFormValues>({
    defaultValues: { searchQuery: '' },
  })

  const [searchedOfferName, setSearchedOfferName] = useState('')

  const { handleSubmit: handleSubmitSearch } = form

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
      onError: () => {
        notify.error(GET_DATA_ERROR_MESSAGE)
      },
    }
  )

  const [isCreatingNewOffer, setIsCreatingNewOffer] = useState(false)

  const handleOfferCardSelected = async (offerId: number) => {
    setIsCreatingNewOffer(true)

    await createOfferFromTemplate(
      navigate,
      notify,
      offerId,
      undefined,
      isMarseilleActive,
      setIsCreatingNewOffer
    )
  }

  return (
    <BasicLayout
      mainHeading="Créer une offre réservable"
      isStickyActionBarInChild
    >
      {isCreatingNewOffer ? (
        <div className="container">
          <Spinner message="Création de la nouvelle offre réservable en cours" />
        </div>
      ) : (
        <div className="container">
          <div className={styles['search-container']}>
            <form
              className={styles['search-input-container']}
              aria-labelledby="search-filter"
              onSubmit={handleSubmitSearch(() => {
                setSearchedOfferName(form.watch('searchQuery'))
              })}
            >
              <div className={styles['search-input']}>
                <TextInput
                  label="Rechercher l’offre vitrine à dupliquer"
                  icon={strokeSearchIcon}
                  {...form.register('searchQuery')}
                  type="search"
                  autoComplete="off"
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
                {/** biome-ignore lint/a11y/useSemanticElements: We want a role status */}
                <p className={styles['visually-hidden']} role="status">
                  {offers && pluralize(offers.length, 'offre vitrine trouvée')}
                </p>

                <p className={styles['legend']}>
                  {searchedOfferName.length === 0
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
                          handleOfferCardSelected(offer.id)
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
      )}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveOfferSelectionDuplication
