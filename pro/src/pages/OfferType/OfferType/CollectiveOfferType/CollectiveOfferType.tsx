import { useFormContext } from 'react-hook-form'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'

import { GetOffererResponseModel } from 'apiClient/v1'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  OFFER_TYPES,
} from 'commons/core/Offers/constants'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { getLastDmsApplicationForOfferer } from 'commons/utils/getLastCollectiveDmsApplication'
import strokeBookedIcon from 'icons/stroke-booked.svg'
import strokeDuplicateOfferIcon from 'icons/stroke-duplicate-offer.svg'
import strokeNewOfferIcon from 'icons/stroke-new-offer.svg'
import strokeTemplateOfferIcon from 'icons/stroke-template-offer.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'

import styles from './CollectiveOfferType.module.scss'

interface CollectiveOfferTypeProps {
  offerer: GetOffererResponseModel | null
}

export const CollectiveOfferType = ({ offerer }: CollectiveOfferTypeProps) => {
  const location = useLocation()
  const { setValue, getValues } = useFormContext()

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
          variant="detailed"
          name="collectiveOfferSubtype"
          className={styles['container']}
          legend={
            <h2 className={styles['legend']}>Quel est le type de l’offre ?</h2>
          }
          onChange={(e) =>
            setValue('offer.collectiveOfferSubtype', e.target.value)
          }
          checkedOption={getValues('offer.collectiveOfferSubtype')}
          group={[
            {
              label: 'Une offre réservable',
              value: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
              description:
                'Cette offre a une date et un prix. Elle doit être associée à un établissement scolaire avec lequel vous avez préalablement échangé.',
              asset: {
                variant: 'icon',
                src: strokeBookedIcon,
              },
            },
            {
              label: 'Une offre vitrine',
              value: COLLECTIVE_OFFER_SUBTYPE.TEMPLATE,
              description:
                'Cette offre n’est pas réservable. Elle permet aux enseignants de vous contacter pour co-construire une offre adaptée. Vous pourrez facilement la dupliquer pour chaque enseignant intéressé.',
              asset: {
                variant: 'icon',
                src: strokeTemplateOfferIcon,
              },
            },
          ]}
        />
      )}

      {offerer?.allowedOnAdage &&
        getValues('offer.collectiveOfferSubtype') ===
          COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE && (
          <RadioGroup
            variant="detailed"
            name="collectiveOfferSubtypeDuplicate"
            className={styles['container']}
            legend={
              <h2 className={styles['legend']}>
                Créer une nouvelle offre ou dupliquer une offre ?
              </h2>
            }
            onChange={(e) =>
              setValue('offer.collectiveOfferSubtypeDuplicate', e.target.value)
            }
            checkedOption={getValues('offer.collectiveOfferSubtypeDuplicate')}
            group={[
              {
                label: 'Créer une nouvelle offre',
                value: COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
                description:
                  'Créer une nouvelle offre réservable en partant d’un formulaire vierge.',
                asset: {
                  variant: 'icon',
                  src: strokeNewOfferIcon,
                },
              },
              {
                label: 'Dupliquer les informations d’une offre vitrine',
                value: COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE,
                description:
                  'Créer une offre réservable en dupliquant les informations d’une offre vitrine existante.',
                asset: {
                  variant: 'icon',
                  src: strokeDuplicateOfferIcon,
                },
              },
            ]}
          />
        )}

      {getValues('offer.offerType') === OFFER_TYPES.EDUCATIONAL &&
        !offerer?.isValidated && (
          <Callout className={styles['pending-offerer-callout']}>
            Votre structure est en cours de validation par les équipes pass
            Culture.
          </Callout>
        )}

      {!offerer?.allowedOnAdage && lastDmsApplication && (
        <Callout
          links={[
            {
              href: `/structures/${queryOffererId}/lieux/${lastDmsApplication.venueId}/collectif`,
              label: 'Voir ma demande de référencement',
            },
          ]}
        >
          Vous avez une demande de référencement en cours de traitement
        </Callout>
      )}
    </>
  )
}
