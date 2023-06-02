import { useField } from 'formik'
import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel } from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { IVenue } from 'core/Venue'
import { ReactComponent as ExternalSiteIcon } from 'icons/ico-external-site-filled.svg'
import { ReactComponent as ValidCircleIcon } from 'icons/ico-valid.svg'
import { ReactComponent as ValidIcon } from 'icons/ico-valide-cercle.svg'
import { ButtonLink } from 'ui-kit/Button'
import Button from 'ui-kit/Button/Button'
import { Select } from 'ui-kit/form'
import { Banner, Title } from 'ui-kit/index'

import styles from './PricingPoint.module.scss'

interface PricingPointProps {
  readOnly: boolean
  offerer: GetOffererResponseModel
  venue: IVenue
  setVenueHasPricingPoint: (venueHasPricingPoint: boolean) => void
}

const PricingPoint = ({
  readOnly,
  offerer,
  venue,
  setVenueHasPricingPoint,
}: PricingPointProps) => {
  const [canSubmit, setCanSubmit] = useState(true)
  const [isInputDisabled, setIsInputDisabled] = useState(false)
  const [isConfirmSiretDialogOpen, setIsConfirmSiretDialogOpen] =
    useState(false)
  const [isBannerVisible, setIsBannerVisible] = useState(true)
  const [pricingPointSelectField] = useField({ name: 'venueSiret' })

  useEffect(() => {
    setCanSubmit(!pricingPointSelectField.value)
  }, [pricingPointSelectField.value])

  const handleClick = async () => {
    const pricingPointId = pricingPointSelectField.value
    if (venue?.nonHumanizedId) {
      api
        .linkVenueToPricingPoint(venue.nonHumanizedId, {
          pricingPointId: pricingPointId,
        })
        .then(() => {
          setIsInputDisabled(true)
          setVenueHasPricingPoint(true)
          setIsBannerVisible(false)
          setIsConfirmSiretDialogOpen(false)
        })
    }
  }
  const pricingPointOptions = [
    { value: '', label: 'Sélectionner un lieu dans la liste' },
  ]

  offerer.managedVenues
    ?.filter(venue => venue.siret)
    .forEach(venue =>
      pricingPointOptions.push({
        value: venue.nonHumanizedId.toString(),
        label: `${venue.name} - ${venue.siret}`,
      })
    )

  return (
    <>
      <div className="main-list-title">
        <Title as="h3" className="sub-title" level={4}>
          Barème de remboursement
        </Title>
      </div>
      {!readOnly && !venue.pricingPoint && isBannerVisible && (
        <Banner
          links={[
            {
              href: `https://aide.passculture.app/hc/fr/articles/4413973462929--Acteurs-Culturels-Comment-rattacher-mes-points-de-remboursement-et-mes-coordonn%C3%A9es-bancaires-%C3%A0-un-SIRET-de-r%C3%A9f%C3%A9rence-`,
              linkTitle: 'En savoir plus sur les barèmes de remboursement',
              Icon: ExternalSiteIcon,
            },
          ]}
          type="notification-info"
        >
          Si vous souhaitez vous faire rembourser les offres de votre lieu sans
          SIRET, vous devez sélectionner un lieu avec SIRET dans votre structure
          afin de permettre le calcul de votre barème de remboursement.
          Attention, vous ne pourrez plus modifier votre sélection après
          validation.
        </Banner>
      )}

      {isConfirmSiretDialogOpen && (
        <ConfirmDialog
          cancelText="Annuler"
          confirmText="Valider ma sélection"
          onCancel={() => {
            setIsConfirmSiretDialogOpen(false)
          }}
          onConfirm={handleClick}
          icon={ValidIcon}
          title="Êtes-vous sûr de vouloir sélectionner"
          secondTitle={`ce lieu avec SIRET\u00a0?`}
        >
          <p className={styles['text-dialog']}>
            Vous avez sélectionné un lieu avec SIRET qui sera utilisé pour le
            calcul de vos remboursements
            <br />
            Ce choix ne pourra pas être modifié.
          </p>
          <ButtonLink
            Icon={ExternalSiteIcon}
            link={{
              to: 'https://aide.passculture.app/hc/fr/sections/4411991876241-Modalités-de-remboursements',
              isExternal: true,
            }}
          >
            En savoir plus sur les remboursements
          </ButtonLink>
        </ConfirmDialog>
      )}

      {!readOnly && !venue.pricingPoint && (
        <p className={styles['reimbursement-subtitle']}>
          <span className={styles['text-hightlight']}>
            Sélectionner et valider{' '}
          </span>
          ci-dessous le lieu avec SIRET :
        </p>
      )}

      <div className={styles['dropdown-container']}>
        <div className={`${styles['select']}`}>
          <Select
            disabled={
              venue.pricingPoint?.id ? true : isInputDisabled || readOnly
            }
            id="venueSiret"
            name="venueSiret"
            data-testid={'pricingPointSelect'}
            defaultValue={venue.pricingPoint ? venue.pricingPoint?.id : ''}
            label={
              'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement'
            }
            options={pricingPointOptions}
            hideFooter
          />
        </div>
        {!readOnly && !isInputDisabled && !venue.pricingPoint && (
          <Button
            className={styles['space-left']}
            onClick={() => setIsConfirmSiretDialogOpen(true)}
            disabled={canSubmit}
          >
            Valider la sélection
          </Button>
        )}
        {!readOnly && isInputDisabled && (
          <>
            <ValidCircleIcon className={styles['space-left']} />
            <p
              className={styles['space-text-left']}
              data-testid={'validationText'}
            >
              Sélection validée
            </p>
          </>
        )}
      </div>
    </>
  )
}

export default PricingPoint
