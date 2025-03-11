import { useFormikContext } from 'formik'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  OFFER_TYPES,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
} from 'commons/core/Offers/constants'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { getLastDmsApplicationForOfferer } from 'commons/utils/getLastCollectiveDmsApplication'
import strokeBookedIcon from 'icons/stroke-booked.svg'
import duplicateOfferIcon from 'icons/stroke-duplicate-offer.svg'
import strokeNewOfferIcon from 'icons/stroke-new-offer.svg'
import strokeTemplateOfferIcon from 'icons/stroke-template-offer.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { RadioGroup } from 'ui-kit/form/RadioGroup/RadioGroup'
import { RadioVariant } from 'ui-kit/form/shared/BaseRadio/BaseRadio'

import { OfferTypeFormValues } from '../types'

import styles from './CollectiveOfferType.module.scss'

interface CollectiveOfferTypeProps {
  offerer: GetOffererResponseModel | null
}

export const CollectiveOfferType = ({ offerer }: CollectiveOfferTypeProps) => {
  const location = useLocation()
  const { values } = useFormikContext<OfferTypeFormValues>()

  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = useSelector(selectCurrentOffererId)
  const queryVenueId = queryParams.get('lieu')

  const lastDmsApplication = getLastDmsApplicationForOfferer(
    queryVenueId,
    offerer
  )

  return (
    <>
      {offerer?.isValidated && offerer.allowedOnAdage && (
        <RadioGroup
          name="collectiveOfferSubtype"
          className={styles['container']}
          legend={
            <h2 className={styles['legend']}>Quel est le type de l’offre ?</h2>
          }
          group={[
            {
              label: 'Une offre réservable',
              value: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
              description:
                'Cette offre a une date et un prix. Elle doit être associée à un établissement scolaire avec lequel vous avez préalablement échangé.',
              icon: strokeBookedIcon,
            },
            {
              label: 'Une offre vitrine',
              value: COLLECTIVE_OFFER_SUBTYPE.TEMPLATE,
              description:
                'Cette offre n’est pas réservable. Elle permet aux enseignants de vous contacter pour co-construire une offre adaptée. Vous pourrez facilement la dupliquer pour chaque enseignant intéressé.',
              icon: strokeTemplateOfferIcon,
            },
          ]}
          variant={RadioVariant.BOX}
        />
      )}
      {offerer?.allowedOnAdage &&
        values.collectiveOfferSubtype ===
          COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE && (
          <RadioGroup
            name="collectiveOfferSubtypeDuplicate"
            className={styles['container']}
            legend={
              <h2 className={styles['legend']}>
                Créer une nouvelle offre ou dupliquer une offre ?
              </h2>
            }
            group={[
              {
                label: 'Créer une nouvelle offre',
                value: COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
                description:
                  'Créer une nouvelle offre réservable en partant d’un formulaire vierge.',
                icon: strokeNewOfferIcon,
              },
              {
                label: 'Dupliquer les informations d’une offre vitrine',
                value: COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE,
                description:
                  'Créer une offre réservable en dupliquant les informations d’une offre vitrine existante.',
                icon: duplicateOfferIcon,
              },
            ]}
            variant={RadioVariant.BOX}
          />
        )}
      {values.offerType === OFFER_TYPES.EDUCATIONAL &&
        !offerer?.isValidated && (
          <Callout
            variant={CalloutVariant.INFO}
            className={styles['pending-offerer-callout']}
          >
            Votre structure est en cours de validation par les équipes pass
            Culture.
          </Callout>
        )}
      {!offerer?.allowedOnAdage &&
        (lastDmsApplication && (
          <Callout
            variant={CalloutVariant.INFO}
            links={[
              {
                href: `/structures/${queryOffererId}/lieux/${lastDmsApplication.venueId}/collectif`,
                label: 'Voir ma demande de référencement',
              },
            ]}
          >
            Vous avez une demande de référencement en cours de traitement
          </Callout>
        ))}
    </>
  )
}
