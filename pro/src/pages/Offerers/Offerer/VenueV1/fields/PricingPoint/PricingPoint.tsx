import * as Sentry from '@sentry/react'
import cn from 'classnames'
import { useState } from 'react'
import { useFormContext } from 'react-hook-form'

import { api } from '@/apiClient/api'
import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import type { SelectOption } from '@/commons/custom_types/form'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ConfirmDialog } from '@/components/ConfirmDialog/ConfirmDialog'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeValidIcon from '@/icons/stroke-valid.svg'
import type { VenueSettingsFormValues } from '@/pages/VenueSettings/commons/types'
import { Select } from '@/ui-kit/form/Select/Select'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './PricingPoint.module.scss'

export interface PricingPointProps {
  offerer: GetOffererResponseModel
  venue: GetVenueResponseModel
}

export const PricingPoint = ({ offerer, venue }: PricingPointProps) => {
  const [isInputDisabled, setIsInputDisabled] = useState(false)
  const [isConfirmSiretDialogOpen, setIsConfirmSiretDialogOpen] =
    useState(false)
  const [isBannerVisible, setIsBannerVisible] = useState(true)
  const [isSubmitingPricingPoint, setIsSubmitingPricingPoint] = useState(false)
  const snackBar = useSnackBar()
  const {
    register,
    watch,
    formState: { errors },
  } = useFormContext<VenueSettingsFormValues>()

  const venueSiret = watch('venueSiret')

  const handleClick = async () => {
    if (venue.id) {
      setIsSubmitingPricingPoint(true)
      try {
        await api.linkVenueToPricingPoint(venue.id, {
          pricingPointId: Number(venueSiret),
        })
        setIsInputDisabled(true)
        setIsBannerVisible(false)
        setIsConfirmSiretDialogOpen(false)
      } catch (error) {
        snackBar.error(SENT_DATA_ERROR_MESSAGE)
        Sentry.captureException(error)
      }
      setIsSubmitingPricingPoint(false)
    }
  }

  const pricingPointOptions: SelectOption[] =
    offerer?.managedVenues
      ?.filter((venue) => Boolean(venue.siret))
      .map((venue) => ({
        label: `${venue.name} - ${venue.siret}`,
        value: venue.id.toString(),
      })) ?? []

  return (
    <>
      {!venue.pricingPoint && isBannerVisible && (
        <div className={`${styles['desk-callout']}`}>
          <Banner
            title="Structure SIRET requise"
            actions={[
              {
                href: `https://aide.passculture.app/hc/fr/articles/4413973462929--Acteurs-Culturels-Comment-rattacher-mes-points-de-remboursement-et-mes-coordonn%C3%A9es-bancaires-%C3%A0-un-SIRET-de-r%C3%A9f%C3%A9rence-`,
                label: `Comment ajouter vos coordonnées bancaires sur une structure sans SIRET ?`,
                isExternal: true,
                icon: fullLinkIcon,
                iconAlt: 'Nouvelle fenêtre',
                type: 'link',
              },
            ]}
            description="Pour le remboursement des offres sans SIRET, sélectionnez une structure avec SIRET dans votre entité. Cette sélection sera définitive après validation."
          />
        </div>
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
        secondTitle={`cette structure avec SIRET\u00a0?`}
        isLoading={isSubmitingPricingPoint}
        open={isConfirmSiretDialogOpen}
      >
        <p className={styles['text-dialog']}>
          Vous avez sélectionné une structure avec SIRET qui sera utilisée pour
          le calcul de vos remboursements
          <br />
          Ce choix ne pourra pas être modifié.
        </p>
        <Button
          as="a"
          icon={fullLinkIcon}
          to="https://aide.passculture.app/hc/fr/sections/4411991876241-Modalités-de-remboursements"
          isExternal
          label="En savoir plus sur les remboursements"
        />
      </ConfirmDialog>

      {!venue.pricingPoint && (
        <p className={styles['reimbursement-subtitle']}>
          <span className={styles['text-hightlight']}>
            Sélectionner et valider{' '}
          </span>
          ci-dessous la structure avec SIRET :
        </p>
      )}

      <div className={styles['dropdown-container']}>
        <div className={styles['select']}>
          <Select
            {...register('venueSiret')}
            disabled={venue.pricingPoint?.id ? true : isInputDisabled}
            data-testid={'pricingPointSelect'}
            label="Structure avec SIRET utilisée pour le calcul de votre barème de remboursement"
            options={[
              {
                value: '',
                label: 'Sélectionner une structure dans la liste',
              },
              ...pricingPointOptions,
            ]}
            required={true}
            error={errors.venueSiret?.message}
          />
        </div>
        {!isInputDisabled && !venue.pricingPoint && (
          <div className={styles['space-left']}>
            <Button
              onClick={() => setIsConfirmSiretDialogOpen(true)}
              disabled={!venueSiret}
              label="Valider la sélection"
            />
          </div>
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
