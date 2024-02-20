import { useEffect, useState } from 'react'

import { CollectiveOfferResponseModel } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import Callout from 'components/Callout/Callout'
import strokeMyInstitution from 'icons/stroke-my-institution.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'
import Offer from '../OffersInstantSearch/OffersSearch/Offers/Offer'

import styles from './OffersForMyInstitution.module.scss'

const OffersForMyInstitution = (): JSX.Element => {
  const params = new URLSearchParams(location.search)
  const adageAuthToken = params.get('token')
  const [myInstitutionOffers, setMyInstitutionOffers] = useState<
    CollectiveOfferResponseModel[]
  >([])
  const [loadingOffers, setLoadingOffers] = useState<boolean>(false)

  useEffect(() => {
    async function getMyInstitutionOffers() {
      setLoadingOffers(true)
      try {
        const offers = await apiAdage.getCollectiveOffersForMyInstitution()

        setMyInstitutionOffers(
          offers.collectiveOffers.map((offer) => ({
            ...offer,
            isTemplate: false,
          }))
        )
      } catch (e) {
        sendSentryCustomError(e)
      } finally {
        setLoadingOffers(false)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getMyInstitutionOffers()
  }, [])

  if (loadingOffers) {
    return <Spinner message="Chargement en cours" />
  }

  return (
    <AnalyticsContextProvider>
      <h1>Pour mon établissement</h1>
      <Callout
        className={styles['my-institution-callout']}
        links={[
          {
            href: `${document.referrer}adage/passculture/index`,
            isExternal: true,
            label: 'Voir la page “Suivi pass Culture”',
          },
        ]}
      >
        <p className={styles['callout-text']}>
          Retrouvez sur cette page les offres destinées aux professeurs de votre
          établissement et rédigées par les acteurs culturels partenaires de
          l’établissement scolaire.
        </p>
        <p className={styles['callout-text']}>
          Le contenu, la date et le montant de chaque offre ont été définis lors
          d’échanges entre un professeur et la structure culturelle concernée.
        </p>
        <p>
          Processus : vous cliquez sur “Préréserver” l’offre qui vous est
          destinée. L’offre va disparaitre de cette page, mais vous pourrez la
          retrouver dans la page “Suivi pass Culture”. Puis, vous associerez
          l’offre à votre projet pédagogique dans la page “Les projets”. Enfin,
          votre chef d’établissement confirmera la réservation de l’offre dans
          “Suivi pass Culture”.
        </p>
      </Callout>
      {myInstitutionOffers.length === 0 ? (
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
        <ul className={styles['offers-list']}>
          {myInstitutionOffers.map((offer, i) => {
            return (
              <li key={offer.id} data-testid="offer-listitem">
                <Offer offer={offer} queryId="" position={i}></Offer>
              </li>
            )
          })}
        </ul>
      )}
    </AnalyticsContextProvider>
  )
}

export default OffersForMyInstitution
