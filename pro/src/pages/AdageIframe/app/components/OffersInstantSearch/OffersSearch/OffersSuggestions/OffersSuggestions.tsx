import { ReactNode } from 'react'
import { Configure, Index, useInstantSearch } from 'react-instantsearch'

import { OfferAddressType } from 'apiClient/adage'
import { useAdageUser } from 'pages/AdageIframe/app/hooks/useAdageUser'
import { ALGOLIA_COLLECTIVE_OFFERS_INDEX } from 'utils/config'
import { isNumber } from 'utils/types'

import {
  algoliaSearchDefaultAttributesToRetrieve,
  DEFAULT_GEO_RADIUS,
  SearchFormValues,
} from '../../OffersInstantSearch'
import { adageFiltersToFacetFilters } from '../../utils'
import { Offers } from '../Offers/Offers'

import styles from './OffersSuggestions.module.scss'
import { OffersSuggestionsHeader } from './OffersSuggestionsHeader/OffersSuggestionsHeader'

export type OffersSuggestionsProps = {
  formValues: SearchFormValues
}

function getSearchIndexIdDisplayed(
  scopedResults: ReturnType<typeof useInstantSearch>['scopedResults']
): string | null {
  //  Only keep indexes relative to no result
  const noResultIndexesResults = scopedResults.filter((scopedRes) =>
    scopedRes.indexId.startsWith('no_results_offers_index_')
  )

  noResultIndexesResults.sort((resA, resB) => {
    return (
      Number(resA.indexId.split('_').pop()) -
      Number(resB.indexId.split('_').pop())
    )
  })

  //  Find first index that has results
  for (const result of noResultIndexesResults) {
    // react-instantsearch results mignt be null but the lib does not
    // export a SearchResults type that we could use to make sure of that
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
    if (result.results?.nbHits > 0) {
      return result.indexId
    }
  }

  return null
}

const getPossibleFilterValues = (
  formValues: SearchFormValues
): { values: SearchFormValues; headerMessage: ReactNode }[] => {
  const possibleFacetFilters = []
  //  The returned array should be in the order of preferred suggestion filters

  if (formValues.formats.length !== 0) {
    possibleFacetFilters.push({
      values: {
        ...formValues,
        eventAddressType: OfferAddressType.OTHER,
        domains: [],
        categories: [],
        formats: [],
        geolocRadius: DEFAULT_GEO_RADIUS,
      },
      headerMessage: 'Découvrez des offres qui relèvent d’autres formats',
    })
  }

  if (formValues.domains.length !== 0) {
    possibleFacetFilters.push({
      values: {
        ...formValues,
        eventAddressType: OfferAddressType.OTHER,
        domains: [],
        geolocRadius: DEFAULT_GEO_RADIUS,
      },
      headerMessage:
        'Découvrez des offres qui relèvent d’autres domaines artistiques',
    })
  }

  if (formValues.eventAddressType !== OfferAddressType.OTHER) {
    possibleFacetFilters.push({
      values: {
        ...formValues,
        eventAddressType: OfferAddressType.OTHER,
        geolocRadius: DEFAULT_GEO_RADIUS,
      },
      headerMessage:
        'Découvrez des offres qui relèvent d’autres types d’intervention',
    })
  }

  possibleFacetFilters.push(
    {
      values: {
        ...formValues,
        geolocRadius: 5000,
        domains: [],
        categories: [],
        formats: [],
        eventAddressType: OfferAddressType.OTHER,
      },
      headerMessage:
        ' Découvrez des propositions de sorties scolaires à proximité de votre établissement',
    },
    {
      values: {
        ...formValues,
        geolocRadius: 100_000,
        domains: [],
        categories: [],
        formats: [],
        eventAddressType: OfferAddressType.OFFERER_VENUE,
      },
      headerMessage:
        'Découvrez les offres de partenaires culturels locaux prêts à intervenir dans votre classe',
    }
  )

  return possibleFacetFilters.map((elm) => {
    return { ...elm, departments: [], academies: [] }
  })
}

export const OffersSuggestions = ({ formValues }: OffersSuggestionsProps) => {
  const { adageUser } = useAdageUser()
  const { scopedResults } = useInstantSearch()
  const searchIndexIdDisplayed: null | string =
    getSearchIndexIdDisplayed(scopedResults)

  const formValuesArray: {
    values: SearchFormValues
    headerMessage: ReactNode
  }[] = getPossibleFilterValues(formValues)

  return (
    <>
      {formValuesArray.map((formValues, i) => {
        return (
          <Index
            indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
            indexId={`no_results_offers_index_${i}`}
            key={i}
          >
            <Configure
              attributesToHighlight={[]}
              attributesToRetrieve={algoliaSearchDefaultAttributesToRetrieve}
              clickAnalytics
              facetFilters={[
                [
                  'offer.educationalInstitutionUAICode:all',
                  `offer.educationalInstitutionUAICode:${adageUser.uai}`,
                ],
                ...adageFiltersToFacetFilters(formValues.values).queryFilters,
              ]}
              query={''}
              filters={
                'offer.eventAddressType:offererVenue<score=3> OR offer.eventAddressType:school<score=2> OR offer.eventAddressType:other<score=1>'
              }
              hitsPerPage={3}
              aroundLatLng={
                isNumber(adageUser.lat) && isNumber(adageUser.lon)
                  ? `${adageUser.lat}, ${adageUser.lon}`
                  : undefined
              }
              aroundRadius={formValues.values.geolocRadius}
              distinct={false}
            />
            {searchIndexIdDisplayed === `no_results_offers_index_${i}` && (
              <div className={styles['offers-suggestions']}>
                <OffersSuggestionsHeader>
                  {formValues.headerMessage}
                </OffersSuggestionsHeader>
                <Offers
                  displayShowMore={false}
                  displayStats={false}
                  displayNoResult={false}
                  indexId={`no_results_offers_index_${i}`}
                />
              </div>
            )}
          </Index>
        )
      })}
    </>
  )
}
