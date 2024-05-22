import { useFormikContext } from 'formik'
import { useLocation } from 'react-router-dom'

import { GetOffererResponseModel } from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  OFFER_TYPES,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
} from 'core/Offers/constants'
import strokeBookedIcon from 'icons/stroke-booked.svg'
import duplicateOfferIcon from 'icons/stroke-duplicate-offer.svg'
import strokeNewOfferIcon from 'icons/stroke-new-offer.svg'
import strokeTemplateOfferIcon from 'icons/stroke-template-offer.svg'
import { Banner } from 'ui-kit/Banners/Banner/Banner'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'
import { getLastDmsApplicationForOfferer } from 'utils/getLastCollectiveDmsApplication'

import styles from '../OfferType.module.scss'
import { OfferTypeFormValues } from '../types'

interface CollectiveOfferTypeProps {
  offerer?: GetOffererResponseModel
}

const CollectiveOfferType = ({ offerer }: CollectiveOfferTypeProps) => {
  const location = useLocation()
  const { values, handleChange } = useFormikContext<OfferTypeFormValues>()

  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = queryParams.get('structure')
  const queryVenueId = queryParams.get('lieu')

  const lastDmsApplication = getLastDmsApplicationForOfferer(
    queryVenueId,
    offerer
  )

  return (
    <>
      {offerer?.isValidated && offerer.allowedOnAdage && (
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
      {offerer?.allowedOnAdage &&
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

      {values.offerType === OFFER_TYPES.EDUCATIONAL &&
        !offerer?.isValidated && (
          <Banner>
            Votre structure est en cours de validation par les équipes pass
            Culture.
          </Banner>
        )}
      {!offerer?.allowedOnAdage &&
        (lastDmsApplication ? (
          <Banner
            links={[
              {
                href: `/structures/${queryOffererId}/lieux/${lastDmsApplication.venueId}/collectif`,
                label: 'Voir ma demande de référencement',
              },
            ]}
          >
            Vous avez une demande de référencement en cours de traitement
          </Banner>
        ) : (
          <Callout
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
            variant={CalloutVariant.ERROR}
          >
            Pour proposer des offres à destination d’un groupe scolaire, vous
            devez être référencé auprès du ministère de l’Éducation Nationale et
            du ministère de la Culture.
          </Callout>
        ))}
    </>
  )
}

export default CollectiveOfferType
