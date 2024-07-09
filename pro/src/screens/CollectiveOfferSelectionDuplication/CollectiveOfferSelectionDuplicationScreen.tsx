import cn from 'classnames'
import { Form, FormikProvider, useFormik } from 'formik'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
} from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { createOfferFromTemplate } from 'core/OfferEducational/utils/createOfferFromTemplate'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { computeOffersUrl } from 'core/Offers/utils/computeOffersUrl'
import { serializeApiFilters } from 'core/Offers/utils/serializer'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { useActiveFeature } from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { RadioButton } from 'ui-kit/form/RadioButton/RadioButton'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Thumb } from 'ui-kit/Thumb/Thumb'
import { Titles } from 'ui-kit/Titles/Titles'
import { pluralize } from 'utils/pluralize'

import styles from './CollectiveOfferSelectionDuplication.module.scss'

export const CollectiveOfferSelectionDuplication = (): JSX.Element => {
  const [isLoading, setIsLoading] = useState(false)
  const [offers, setOffers] = useState<CollectiveOfferResponseModel[]>([])
  const [showAll, setShowAll] = useState(true)
  const notify = useNotification()
  const navigate = useNavigate()
  const isMarseilleActive = useActiveFeature('WIP_ENABLE_MARSEILLE')
  const formikSearch = useFormik({
    initialValues: { searchFilter: '' },
    onSubmit: (formValues) =>
      filterTemplateOfferByName(formValues.searchFilter),
  })
  const formikSelection = useFormik({
    initialValues: { templateOfferId: '' },
    onSubmit: () => handleOnSubmit(),
  })
  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = queryParams.get('structure')
  const queryVenueId = queryParams.get('lieu')

  const filterTemplateOfferByName = useCallback(
    async (offerName: string) => {
      setIsLoading(true)
      const {
        nameOrIsbn,
        offererId,
        venueId,
        categoryId,
        status,
        creationMode,
        periodBeginningDate,
        periodEndingDate,
        collectiveOfferType,
        format,
      } = serializeApiFilters({
        ...DEFAULT_SEARCH_FILTERS,
        nameOrIsbn: offerName,
        collectiveOfferType: 'template',
        offererId: queryOffererId ? queryOffererId : 'all',
        venueId: queryVenueId ? queryVenueId : 'all',
      })

      try {
        const offers = await api.getCollectiveOffers(
          nameOrIsbn,
          offererId,
          status as CollectiveOfferDisplayedStatus,
          venueId,
          categoryId,
          creationMode,
          periodBeginningDate,
          periodEndingDate,
          collectiveOfferType,
          format
        )

        if (offerName.length < 1) {
          setShowAll(true)
        } else {
          setShowAll(false)
        }

        setOffers(offers)
        setIsLoading(false)
      } catch (error) {
        setIsLoading(false)
        return notify.error(GET_DATA_ERROR_MESSAGE)
      }
    },
    [notify]
  )

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    filterTemplateOfferByName(formikSearch.initialValues.searchFilter)
  }, [formikSearch.initialValues.searchFilter])

  const handleOnSubmit = () => {
    const templateOfferId = formikSelection.values.templateOfferId
    if (templateOfferId === '') {
      return notify.error(
        'Vous devez séléctionner une offre vitrine à dupliquer'
      )
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    createOfferFromTemplate(
      navigate,
      notify,
      Number(templateOfferId),
      undefined,
      isMarseilleActive
    )
  }

  return (
    <AppLayout layout={'sticky-actions'}>
      <div className="container">
        <Titles title="Créer une offre réservable" />
        <h2 className={styles['sub-title']} id="search-filter">
          Rechercher l’offre vitrine à dupliquer
        </h2>

        <div className={styles['search-container']}>
          <FormikProvider value={formikSearch}>
            <Form className={styles['search-input-container']}>
              <TextInput
                label="Offre vitrine à dupliquer"
                isLabelHidden
                name="searchFilter"
                placeholder="Rechercher une offre vitrine"
                className={styles['search-input']}
                aria-labelledby="search-filter"
              />
              <Button
                type="submit"
                className={styles['search-button']}
                isLoading={isLoading}
                aria-label="Button de recherche"
                icon={strokeSearchIcon}
              >
                Rechercher
              </Button>
            </Form>
          </FormikProvider>
          <FormikProvider value={formikSelection}>
            <Form>
              <fieldset>
                <legend>
                  <p className={styles['offer-info']}>
                    {showAll
                      ? 'Les dernières offres vitrines créées'
                      : `${pluralize(offers.length, 'offre')} vitrine`}
                  </p>
                </legend>

                {offers.slice(0, 5).map((offer) => (
                  <div
                    key={offer.id}
                    className={cn(styles['offer-selection'], {
                      [styles['offer-selected']]:
                        formikSelection.values.templateOfferId ===
                        offer.id.toString(),
                    })}
                  >
                    <RadioButton
                      name="templateOfferId"
                      value={offer.id.toString()}
                      label={
                        <div className={styles['offer-selection-label']}>
                          <Thumb
                            url={offer.imageUrl}
                            className={styles['img-offer']}
                          />
                          <p className={styles['offer-title']}>
                            <strong>{offer.name}</strong>
                            {offer.venue.name}
                          </p>
                        </div>
                      }
                    />
                  </div>
                ))}
              </fieldset>
              {offers.length < 1 && (
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
                    to={computeOffersUrl({})}
                  >
                    Annuler et quitter
                  </ButtonLink>
                </ActionsBarSticky.Left>
                <ActionsBarSticky.Right>
                  <Button type="submit" disabled={false}>
                    Étape suivante
                  </Button>
                </ActionsBarSticky.Right>
              </ActionsBarSticky>
            </Form>
          </FormikProvider>
        </div>
      </div>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = CollectiveOfferSelectionDuplication
