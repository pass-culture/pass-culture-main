import * as Sentry from '@sentry/react'
import cn from 'classnames'
import { useField, useFormikContext } from 'formik'
import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOffererResponseModel, GetVenueResponseModel } from 'apiClient/v1'
import { SENT_DATA_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import fullLinkIcon from 'icons/full-link.svg'
import strokeValidIcon from 'icons/stroke-valid.svg'
import { type VenueSettingsFormValues } from 'pages/VenueSettings/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { Callout } from 'ui-kit/Callout/Callout'
import { Select } from 'ui-kit/form/Select/Select'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './PricingPoint.module.scss'

export interface PricingPointProps {
  offerer: GetOffererResponseModel
  venue: GetVenueResponseModel
}

export const PricingPoint = ({ offerer, venue }: PricingPointProps) => {
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const [canSubmit, setCanSubmit] = useState(true)
  const [isInputDisabled, setIsInputDisabled] = useState(false)
  const [isConfirmSiretDialogOpen, setIsConfirmSiretDialogOpen] =
    useState(false)
  const [isBannerVisible, setIsBannerVisible] = useState(true)
  const [pricingPointSelectField] = useField({ name: 'venueSiret' })
  const [isSubmitingPricingPoint, setIsSubmitingPricingPoint] = useState(false)
  const notify = useNotification()
  const formik = useFormikContext<VenueSettingsFormValues>()

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
  const pricingPointOptions: SelectOption[] = [
    {
      value: '',
      label: `Sélectionner ${isOfferAddressEnabled ? 'une structure' : 'un lieu'} dans la liste`,
    },
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
              label: `Comment ajouter vos coordonnées bancaires sur ${isOfferAddressEnabled ? 'une structure' : 'un lieu'} sans SIRET ?`,
              isExternal: true,
            },
          ]}
          className={`${styles['desk-callout']}`}
        >
          Si vous souhaitez vous faire rembourser les offres de votre{' '}
          {isOfferAddressEnabled ? 'structure' : 'lieu'} sans SIRET, vous devez
          sélectionner {isOfferAddressEnabled ? 'une structure' : 'un lieu'}{' '}
          avec SIRET dans votre {isOfferAddressEnabled ? 'entité' : 'structure'}{' '}
          afin de permettre le calcul de votre barème de remboursement.
          Attention, vous ne pourrez plus modifier votre sélection après
          validation.
        </Callout>
      )}

      <ConfirmDialog
        cancelText="Annuler"
        confirmText="Valider ma sélection"
        onCancel={() => {
          setIsConfirmSiretDialogOpen(false)
        }}
        onConfirm={handleClick}
        icon={strokeValidIcon}
        title="Êtes-vous sûr de vouloir sélectionner"
        secondTitle={`${isOfferAddressEnabled ? 'cette structure' : 'ce lieu'} avec SIRET\u00a0?`}
        isLoading={isSubmitingPricingPoint}
        open={isConfirmSiretDialogOpen}
      >
        <p className={styles['text-dialog']}>
          Vous avez sélectionné{' '}
          {isOfferAddressEnabled
            ? 'une structure avec SIRET qui sera utilisée'
            : 'un lieu avec SIRET qui sera utilisé'}{' '}
          pour le calcul de vos remboursements
          <br />
          Ce choix ne pourra pas être modifié.
        </p>
        <ButtonLink
          icon={fullLinkIcon}
          to="https://aide.passculture.app/hc/fr/sections/4411991876241-Modalités-de-remboursements"
          isExternal
        >
          En savoir plus sur les remboursements
        </ButtonLink>
      </ConfirmDialog>

      {!venue.pricingPoint && (
        <p className={styles['reimbursement-subtitle']}>
          <span className={styles['text-hightlight']}>
            Sélectionner et valider{' '}
          </span>
          ci-dessous {isOfferAddressEnabled ? 'la structure' : 'le lieu'} avec
          SIRET :
        </p>
      )}

      <div className={styles['dropdown-container']}>
        <div className={styles['select']}>
          <Select
            disabled={venue.pricingPoint?.id ? true : isInputDisabled}
            id="venueSiret"
            name="venueSiret"
            data-testid={'pricingPointSelect'}
            onChange={formik.handleChange}
            label={`${isOfferAddressEnabled ? 'Structure avec SIRET utilisée' : 'Lieu avec SIRET utilisé'} pour le calcul de votre barème de remboursement`}
            options={pricingPointOptions}
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
