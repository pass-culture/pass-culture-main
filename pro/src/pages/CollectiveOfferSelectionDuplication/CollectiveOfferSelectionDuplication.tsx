import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { GET_COLLECTIVE_OFFERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { createOfferFromTemplate } from '@/commons/core/OfferEducational/utils/createOfferFromTemplate'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { computeCollectiveOffersUrl } from '@/commons/core/Offers/utils/computeCollectiveOffersUrl'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureCurrentOfferer } from '@/commons/store/offerer/selectors'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { SearchInput } from '@/design-system/SearchInput/SearchInput'
import strokeSearchIcon from '@/icons/stroke-search.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { CardLink } from '../../ui-kit/CardLink/CardLink'
import styles from './CollectiveOfferSelectionDuplication.module.scss'
import { SkeletonLoader } from './CollectiveOfferSelectionLoaderSkeleton'

type SearchFormValues = {
  searchQuery: string
}

export const CollectiveOfferSelectionDuplication = (): JSX.Element => {
  const isMarseilleActive = useActiveFeature('ENABLE_MARSEILLE')
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const snackBar = useSnackBar()
  const navigate = useNavigate()

  const form = useForm<SearchFormValues>({
    defaultValues: { searchQuery: '' },
  })

  const [searchedOfferName, setSearchedOfferName] = useState('')

  const { handleSubmit: handleSubmitSearch } = form

  const queryParams = new URLSearchParams(location.search)
  const currentOffererId = useAppSelector(ensureCurrentOfferer).id
  const selectedVenue = useAppSelector(ensureSelectedVenue)
  const queryVenueId = queryParams.get('lieu')

  const {
    name,
    offererId,
    venueId,
    status,
    periodBeginningDate,
    periodEndingDate,
    format,
    locationType,
    offererAddressId,
  } = serializeApiCollectiveFilters({
    ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    name: searchedOfferName,
    offererId: currentOffererId.toString(),
    venueId: withSwitchVenueFeature
      ? selectedVenue.id.toString()
      : (queryVenueId ?? undefined),
    status: [
      CollectiveOfferDisplayedStatus.PUBLISHED,
      CollectiveOfferDisplayedStatus.HIDDEN,
      CollectiveOfferDisplayedStatus.ENDED,
    ],
  })

  const { data: offers, isLoading } = useSWR(
    [GET_COLLECTIVE_OFFERS_QUERY_KEY, name],
    () =>
      api.getCollectiveOfferTemplates(
        name,
        offererId,
        status,
        venueId,
        periodBeginningDate,
        periodEndingDate,
        format,
        locationType,
        offererAddressId
      ),
    {
      onError: () => {
        snackBar.error(GET_DATA_ERROR_MESSAGE)
      },
    }
  )

  const [isCreatingNewOffer, setIsCreatingNewOffer] = useState(false)

  const handleOfferCardSelected = async (offerId: number) => {
    setIsCreatingNewOffer(true)

    await createOfferFromTemplate(
      navigate,
      snackBar,
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
                <SearchInput
                  label="Rechercher l’offre vitrine à dupliquer"
                  {...form.register('searchQuery')}
                  extension={
                    <Button
                      type="submit"
                      disabled={isLoading}
                      label="Rechercher"
                    />
                  }
                />
              </div>
            </form>

            {isLoading ? (
              <SkeletonLoader />
            ) : (
              <>
                {/** biome-ignore lint/a11y/useSemanticElements: We want a `role="status"` here, not an `<output />`. */}
                <p className={styles['visually-hidden']} role="status">
                  {offers && (
                    <>
                      {offers.length}{' '}
                      {pluralizeFr(
                        offers.length,
                        'offre vitrine trouvée',
                        'offres vitrine trouvées'
                      )}
                    </>
                  )}
                </p>

                <p className={styles['legend']}>
                  {searchedOfferName.length === 0
                    ? 'Les dernières offres vitrines créées'
                    : offers && (
                        <>
                          {offers.length}{' '}
                          {pluralizeFr(
                            offers.length,
                            'offre vitrine',
                            'offres vitrine'
                          )}
                        </>
                      )}
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
                    <Button
                      as="a"
                      variant={ButtonVariant.SECONDARY}
                      to={computeCollectiveOffersUrl({})}
                      label="Retour à la liste des offres"
                    />
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
