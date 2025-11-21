import { useFormContext } from 'react-hook-form'
import { useLocation } from 'react-router'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
} from '@/commons/core/Offers/constants'
import { getLastDmsApplicationForOfferer } from '@/commons/utils/getLastCollectiveDmsApplication'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import fullLinkIcon from '@/icons/full-link.svg'
import fullNextIcon from '@/icons/full-next.svg'
import strokeBookedIcon from '@/icons/stroke-booked.svg'
import strokeDuplicateOfferIcon from '@/icons/stroke-duplicate-offer.svg'
import strokeNewOfferIcon from '@/icons/stroke-new-offer.svg'
import strokeTemplateOfferIcon from '@/icons/stroke-template-offer.svg'

import styles from './CollectiveOfferType.module.scss'

interface CollectiveOfferTypeProps {
  offerer: GetOffererResponseModel | null
}

export const CollectiveOfferType = ({ offerer }: CollectiveOfferTypeProps) => {
  const location = useLocation()
  const { setValue, getValues, watch } = useFormContext()

  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = offerer?.id
  const queryVenueId = queryParams.get('lieu')

  const lastDmsApplication = getLastDmsApplicationForOfferer(
    queryVenueId,
    offerer
  )

  return (
    <>
      {offerer?.isValidated && offerer.allowedOnAdage && (
        <div className={styles['container']}>
          <RadioButtonGroup
            variant="detailed"
            name={watch('offer.collectiveOfferSubtype')}
            label={
              <h2 className={styles['radio-group-title']}>
                Quel est le type de l’offre ?
              </h2>
            }
            onChange={(e) =>
              setValue('offer.collectiveOfferSubtype', e.target.value)
            }
            checkedOption={getValues('offer.collectiveOfferSubtype')}
            options={[
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
        </div>
      )}

      {offerer?.allowedOnAdage &&
        getValues('offer.collectiveOfferSubtype') ===
          COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE && (
          <div className={styles['container']}>
            <RadioButtonGroup
              variant="detailed"
              name={watch('offer.collectiveOfferSubtypeDuplicate')}
              label={
                <h2 className={styles['radio-group-title']}>
                  Créer une nouvelle offre ou dupliquer une offre ?
                </h2>
              }
              sizing="fill"
              onChange={(e) =>
                setValue(
                  'offer.collectiveOfferSubtypeDuplicate',
                  e.target.value
                )
              }
              checkedOption={getValues('offer.collectiveOfferSubtypeDuplicate')}
              options={[
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
          </div>
        )}

      {!offerer?.isValidated && (
        <div className={styles['pending-offerer-callout']}>
          <Banner
            title=""
            description="Votre structure est en cours de validation par les équipes pass Culture."
          />
        </div>
      )}

      {!offerer?.allowedOnAdage &&
        (lastDmsApplication ? (
          <div className={styles['pending-offerer-callout']}>
            <Banner
              title=""
              actions={[
                {
                  href: `/structures/${queryOffererId}/lieux/${lastDmsApplication.venueId}/collectif`,
                  label: 'Voir ma demande de référencement',
                  type: 'link',
                  icon: fullNextIcon,
                },
              ]}
              description="Vous avez une demande de référencement en cours de traitement"
            />
          </div>
        ) : (
          <div className={styles['pending-offerer-callout']}>
            <Banner
              title=""
              actions={[
                {
                  href: 'https://demarche.numerique.gouv.fr/commencer/demande-de-referencement-sur-adage',
                  label: 'Faire une demande de référencement',
                  isExternal: true,
                  icon: fullLinkIcon,
                  iconAlt: 'Nouvelle fenêtre',
                  type: 'link',
                },
                {
                  href: 'https://aide.passculture.app/hc/fr/articles/5700215550364',
                  label:
                    'Ma demande de référencement a été acceptée mais je ne peux toujours pas créer d’offres collectives',
                  isExternal: true,
                  icon: fullLinkIcon,
                  iconAlt: 'Nouvelle fenêtre',
                  type: 'link',
                },
              ]}
              variant={BannerVariants.ERROR}
              description="Pour proposer des offres à destination d’un groupe scolaire, vous devez être référencé auprès du ministère de l’Éducation Nationale et du ministère de la Culture."
            />
          </div>
        ))}
    </>
  )
}
