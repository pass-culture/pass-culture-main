import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { DMSApplicationForEAC } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  OFFER_TYPES,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import useNotification from 'hooks/useNotification'
import strokeBookedIcon from 'icons/stroke-booked.svg'
import duplicateOfferIcon from 'icons/stroke-duplicate-offer.svg'
import strokeNewOfferIcon from 'icons/stroke-new-offer.svg'
import strokeTemplateOfferIcon from 'icons/stroke-template-offer.svg'
import { getFilteredCollectiveOffersAdapter } from 'pages/CollectiveOffers/adapters'
import { Banner } from 'ui-kit'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'
import Spinner from 'ui-kit/Spinner/Spinner'
import { getLastDmsApplicationForOfferer } from 'utils/getLastCollectiveDmsApplication'

import styles from '../OfferType.module.scss'
import { OfferTypeFormValues } from '../types'

interface CollectiveOfferTypeProps {
  setHasCollectiveTemplateOffer: (arg: boolean) => void
  setIsEligible: (arg: boolean) => void
  isEligible: boolean
}

const CollectiveOfferType = ({
  setHasCollectiveTemplateOffer,
  setIsEligible,
  isEligible,
}: CollectiveOfferTypeProps): JSX.Element => {
  const location = useLocation()
  const notify = useNotification()
  const { values, handleChange } = useFormikContext<OfferTypeFormValues>()

  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = queryParams.get('structure')
  const queryVenueId = queryParams.get('lieu')
  const [isLoading, setIsLoading] = useState(false)
  const [isValidated, setIsValidated] = useState(true)
  const [lastDmsApplication, setLastDmsApplication] = useState<
    DMSApplicationForEAC | null | undefined
  >(null)

  useEffect(() => {
    const getTemplateCollectiveOffers = async () => {
      const apiFilters = {
        ...DEFAULT_SEARCH_FILTERS,
        collectiveOfferType: COLLECTIVE_OFFER_SUBTYPE.TEMPLATE.toLowerCase(),
        offererId: queryOffererId ? queryOffererId : 'all',
        venueId: queryVenueId ? queryVenueId : 'all',
      }
      const { isOk, message, payload } =
        await getFilteredCollectiveOffersAdapter(apiFilters)

      if (!isOk) {
        setHasCollectiveTemplateOffer(false)
        return notify.error(message)
      }

      if (payload.offers.length > 0) {
        setHasCollectiveTemplateOffer(true)
      }
    }

    const checkOffererEligibility = async () => {
      const offererNames = await api.listOfferersNames()

      const offererId = queryOffererId ?? offererNames.offerersNames[0].id
      if (offererNames.offerersNames.length > 1 && !queryOffererId) {
        setIsEligible(true)
        return
      }

      if (offererId) {
        try {
          const { canCreate } = await api.canOffererCreateEducationalOffer(
            Number(offererId)
          )
          setIsEligible(canCreate)
        } catch (error) {
          notify.error(
            'Une erreur technique est survenue lors de la vérification de votre éligibilité.'
          )
        }
      }
    }

    const checkOffererValidation = async () => {
      if (queryOffererId !== null) {
        const response = await api.getOfferer(Number(queryOffererId))
        setIsValidated(response.isValidated)
        const lastDmsApplication = getLastDmsApplicationForOfferer(
          queryVenueId,
          response
        )
        setLastDmsApplication(lastDmsApplication)
      }
    }
    const initializeStates = async () => {
      setIsLoading(true)
      await Promise.all([
        getTemplateCollectiveOffers(),
        checkOffererEligibility(),
        checkOffererValidation(),
      ])
      setIsLoading(false)
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    initializeStates()
  }, [queryOffererId, queryVenueId])

  if (isLoading) {
    return <Spinner />
  }

  return (
    <>
      {isValidated && isEligible && (
        <FormLayout.Section
          title="Quel est le type de l’offre ?"
          className={styles['subtype-section']}
        >
          <FormLayout.Row inline mdSpaceAfter>
            <RadioButtonWithImage
              name="collectiveOfferSubtype"
              icon={strokeBookedIcon}
              isChecked={
                values.collectiveOfferSubtype ===
                COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE
              }
              label="Une offre réservable"
              description="Cette offre a une date et un prix. Elle doit être associée à un établissement scolaire avec lequel vous avez préalablement échangé."
              onChange={handleChange}
              value={COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE}
            />
          </FormLayout.Row>

          <FormLayout.Row inline mdSpaceAfter>
            <RadioButtonWithImage
              name="collectiveOfferSubtype"
              icon={strokeTemplateOfferIcon}
              isChecked={
                values.collectiveOfferSubtype ===
                COLLECTIVE_OFFER_SUBTYPE.TEMPLATE
              }
              label="Une offre vitrine"
              description={`Cette offre n’est pas réservable. Elle permet aux enseignants de vous contacter pour co-construire une offre adaptée. Vous pourrez facilement la dupliquer pour chaque enseignant intéressé.`}
              onChange={handleChange}
              value={COLLECTIVE_OFFER_SUBTYPE.TEMPLATE}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      )}
      {isEligible &&
        values.collectiveOfferSubtype ===
          COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE && (
          <FormLayout.Section
            title="Créer une nouvelle offre ou dupliquer une offre ?"
            className={styles['subtype-section']}
          >
            <FormLayout.Row inline mdSpaceAfter>
              <RadioButtonWithImage
                name="collectiveOfferSubtypeDuplicate"
                icon={strokeNewOfferIcon}
                isChecked={
                  values.collectiveOfferSubtypeDuplicate ===
                  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER
                }
                label="Créer une nouvelle offre"
                description="Créer une nouvelle offre réservable en partant d’un formulaire vierge."
                onChange={handleChange}
                value={COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER}
              />
            </FormLayout.Row>
            <FormLayout.Row inline mdSpaceAfter>
              <RadioButtonWithImage
                name="collectiveOfferSubtypeDuplicate"
                icon={duplicateOfferIcon}
                isChecked={
                  values.collectiveOfferSubtypeDuplicate ===
                  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE
                }
                label="Dupliquer les informations d’une offre vitrine"
                description="Créer une offre réservable en dupliquant les informations d’une offre vitrine existante."
                onChange={handleChange}
                value={COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE}
              />
            </FormLayout.Row>
          </FormLayout.Section>
        )}

      {values.offerType === OFFER_TYPES.EDUCATIONAL && !isValidated && (
        <Banner>
          Votre structure est en cours de validation par les équipes pass
          Culture.
        </Banner>
      )}
      {!isEligible &&
        (lastDmsApplication ? (
          <Banner
            links={[
              {
                href: `/structures/${queryOffererId}/lieux/${lastDmsApplication?.venueId}#venue-collective-data`,
                label: 'Voir ma demande de référencement',
              },
            ]}
          >
            Vous avez une demande de référencement en cours de traitement
          </Banner>
        ) : (
          <Banner
            links={[
              {
                href: 'https://www.demarches-simplifiees.fr/commencer/demande-de-referencement-sur-adage',
                label: 'Faire une demande de référencement',
                isExternal: true,
              },
              {
                href: 'https://aide.passculture.app/hc/fr/articles/5700215550364',
                label:
                  'Ma demande de référencement a été acceptée mais je ne peux toujours pas créer d’offres collectives',
                isExternal: true,
              },
            ]}
          >
            Pour proposer des offres à destination d’un groupe scolaire, vous
            devez être référencé auprès du ministère de l’Éducation Nationale et
            du ministère de la Culture.
          </Banner>
        ))}
    </>
  )
}

export default CollectiveOfferType
