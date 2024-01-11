import algoliasearch from 'algoliasearch/lite'
import React from 'react'
import { Configure, InstantSearch } from 'react-instantsearch'

import Callout from 'components/Callout/Callout'
import fullLinkIcon from 'icons/full-link.svg'
import strokeMyInstitution from 'icons/stroke-my-institution.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import useAdageUser from '../../hooks/useAdageUser'
import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'
import { algoliaSearchDefaultAttributesToRetrieve } from '../OffersInstantSearch/OffersInstantSearch'
import { Offers } from '../OffersInstantSearch/OffersSearch/Offers/Offers'

import styles from './OffersForMyInstitution.module.scss'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

const OffersForMyInstitution = (): JSX.Element => {
  const {
    adageUser: { offersCount, uai },
  } = useAdageUser()
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')

  return (
    <InstantSearch
      indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      searchClient={searchClient}
    >
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={algoliaSearchDefaultAttributesToRetrieve}
        clickAnalytics
        facetFilters={[`offer.educationalInstitutionUAICode:${uai}`]}
        hitsPerPage={8}
        distinct={false}
      />
      <AnalyticsContextProvider>
        <h1>Pour mon établissement</h1>
        <Callout
          className={styles['my-institution-callout']}
          links={[
            {
              href: `${document.referrer}adage/passculture/index`,
              isExternal: true,
              icon: fullLinkIcon,
              linkTitle: 'Voir la page “Suivi pass Culture”',
              svgAlt: 'Nouvelle fenêtre',
            },
          ]}
        >
          <p className={styles['callout-text']}>
            Retrouvez sur cette page les offres destinées aux professeurs de
            votre établissement et rédigées par les acteurs culturels
            partenaires de l’établissement scolaire.
          </p>
          <p>
            Processus : vous cliquez sur “Préréserver” l’offre qui vous est
            destinée. L’offre va disparaitre de cette page, mais vous pourrez la
            retrouver dans la page “Suivi pass Culture”. Puis, vous associerez
            l’offre à votre projet pédagogique dans la page “Les projets”.
            Enfin, votre chef d’établissement confirmera la réservation de
            l’offre dans “Suivi pass Culture”.
          </p>
        </Callout>
        {offersCount === 0 ? (
          <div className={styles['no-results']}>
            <SvgIcon
              src={strokeMyInstitution}
              alt=""
              viewBox="0 0 375 154"
              width="375"
              className={styles['no-results-svg']}
            />
            <div>
              <h2 className={styles['no-results-title']}>
                Vous n’avez pas d’offre à préréserver
              </h2>
              <ButtonLink
                link={{
                  to: `/adage-iframe/recherche?token=${adageAuthToken}`,
                  isExternal: false,
                }}
                variant={ButtonVariant.PRIMARY}
              >
                Explorer le catalogue
              </ButtonLink>
            </div>
          </div>
        ) : (
          <Offers displayStats={false} />
        )}
      </AnalyticsContextProvider>
    </InstantSearch>
  )
}

export default OffersForMyInstitution
