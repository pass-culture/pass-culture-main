import * as Sentry from '@sentry/react'
import cn from 'classnames'
import { useField } from 'formik'
import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel, GetVenueResponseModel } from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import { SENT_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { useNotification } from 'hooks/useNotification'
import fullLinkIcon from 'icons/full-link.svg'
import strokeValidIcon from 'icons/stroke-valid.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { Select } from 'ui-kit/form/Select/Select'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './PricingPoint.module.scss'

export interface PricingPointProps {
  offerer: GetOffererResponseModel
  venue: GetVenueResponseModel
}

export const PricingPoint = ({ offerer, venue }: PricingPointProps) => {
  const [canSubmit, setCanSubmit] = useState(true)
  const [isInputDisabled, setIsInputDisabled] = useState(false)
  const [isConfirmSiretDialogOpen, setIsConfirmSiretDialogOpen] =
    useState(false)
  const [isBannerVisible, setIsBannerVisible] = useState(true)
  const [pricingPointSelectField] = useField({ name: 'venueSiret' })
  const [isSubmitingPricingPoint, setIsSubmitingPricingPoint] = useState(false)
  const notify = useNotification()

  useEffect(() => {
    setCanSubmit(!pricingPointSelectField.value)
  }, [pricingPointSelectField.value])

  const handleClick = async () => {
    const pricingPointId = pricingPointSelectField.value
    if (venue.id) {
      setIsSubmitingPricingPoint(true)
      try {
        await api.linkVenueToPricingPoint(venue.id, {
          pricingPointId: pricingPointId,
        })
        setIsInputDisabled(true)
        setIsBannerVisible(false)
        setIsConfirmSiretDialogOpen(false)
      } catch (error) {
        notify.error(SENT_DATA_ERROR_MESSAGE)
        Sentry.captureException(error)
      }
      setIsSubmitingPricingPoint(false)
    }
  }
  const pricingPointOptions = [
    { value: '', label: 'Sélectionner un lieu dans la liste' },
  ]

  offerer.managedVenues
    ?.filter((venue) => venue.siret)
    .forEach((venue) =>
      pricingPointOptions.push({
        value: venue.id.toString(),
        label: `${venue.name} - ${venue.siret}`,
      })
    )

  return (
    <>
      {!venue.pricingPoint && isBannerVisible && (
        <Callout
          links={[
            {
              href: `https://aide.passculture.app/hc/fr/articles/4413973462929--Acteurs-Culturels-Comment-rattacher-mes-points-de-remboursement-et-mes-coordonn%C3%A9es-bancaires-%C3%A0-un-SIRET-de-r%C3%A9f%C3%A9rence-`,
              label:
                'Comment ajouter vos coordonnées bancaires sur un lieu sans SIRET ?',
              isExternal: true,
            },
          ]}
          className={`${styles['desk-callout']}`}
        >
          Si vous souhaitez vous faire rembourser les offres de votre lieu sans
          SIRET, vous devez sélectionner un lieu avec SIRET dans votre structure
          afin de permettre le calcul de votre barème de remboursement.
          Attention, vous ne pourrez plus modifier votre sélection après
          validation.
        </Callout>
      )}

      {isConfirmSiretDialogOpen && (
        <ConfirmDialog
          cancelText="Annuler"
          confirmText="Valider ma sélection"
          onCancel={() => {
            setIsConfirmSiretDialogOpen(false)
          }}
          onConfirm={handleClick}
          icon={strokeValidIcon}
          title="Êtes-vous sûr de vouloir sélectionner"
          secondTitle={`ce lieu avec SIRET\u00a0?`}
          isLoading={isSubmitingPricingPoint}
        >
          <p className={styles['text-dialog']}>
            Vous avez sélectionné un lieu avec SIRET qui sera utilisé pour le
            calcul de vos remboursements
            <br />
            Ce choix ne pourra pas être modifié.
          </p>
          <ButtonLink
            icon={fullLinkIcon}
            link={{
              to: 'https://aide.passculture.app/hc/fr/sections/4411991876241-Modalités-de-remboursements',
              isExternal: true,
            }}
          >
            En savoir plus sur les remboursements
          </ButtonLink>
        </ConfirmDialog>
      )}

      {!venue.pricingPoint && (
        <p className={styles['reimbursement-subtitle']}>
          <span className={styles['text-hightlight']}>
            Sélectionner et valider{' '}
          </span>
          ci-dessous le lieu avec SIRET :
        </p>
      )}

      <div className={styles['dropdown-container']}>
        <div className={styles['select']}>
          <Select
            disabled={venue.pricingPoint?.id ? true : isInputDisabled}
            id="venueSiret"
            name="venueSiret"
            data-testid={'pricingPointSelect'}
            defaultValue={venue.pricingPoint ? venue.pricingPoint.id : ''}
            label={
              'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement'
            }
            options={pricingPointOptions}
            hideFooter
          />
        </div>
        {!isInputDisabled && !venue.pricingPoint && (
          <Button
            className={styles['space-left']}
            onClick={() => setIsConfirmSiretDialogOpen(true)}
            disabled={canSubmit}
          >
            Valider la sélection
          </Button>
        )}
        {isInputDisabled && (
          <>
            <SvgIcon
              src={strokeValidIcon}
              className={cn(styles['space-left'], styles['siret-valid-icon'])}
              alt=""
              width="24"
            />
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
