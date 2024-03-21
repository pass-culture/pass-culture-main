import React, { useState } from 'react'

import { api } from 'apiClient/api'
import { getHumanReadableApiError } from 'apiClient/helpers'
import { PostVenueProviderBody, VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Button } from 'ui-kit/index'

import { FormValuesProps } from '../AllocineProviderForm/AllocineProviderForm'

import { AllocineProviderFormDialog } from './AllocineProviderFormDialog'
import style from './AllocineProviderParameters.module.scss'

interface AllocineProviderParametersProps {
  venueProvider: VenueProviderResponse
  afterVenueProviderEdit: (editedVenueProvider: VenueProviderResponse) => void
  offererId: number
}

export const AllocineProviderParameters = ({
  venueProvider,
  afterVenueProviderEdit,
  offererId,
}: AllocineProviderParametersProps): JSX.Element => {
  const [isOpenedFormDialog, setIsOpenedFormDialog] = useState(false)
  const notification = useNotification()

  const editVenueProvider = async (
    payload: PostVenueProviderBody
  ): Promise<boolean> => {
    try {
      const editedVenueProvider = await api.updateVenueProvider(payload)
      afterVenueProviderEdit(editedVenueProvider)
      notification.success(
        "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
      )
      return true
    } catch (error) {
      notification.error(getHumanReadableApiError(error))
      return false
    }
  }

  const openFormDialog = () => {
    setIsOpenedFormDialog(true)
  }

  const closeFormDialog = () => {
    setIsOpenedFormDialog(false)
  }

  const onConfirmDialog = async (
    payload: PostVenueProviderBody
  ): Promise<boolean> => {
    const isSuccess = await editVenueProvider({
      ...payload,
      isActive: venueProvider.isActive,
    })

    closeFormDialog()
    return isSuccess
  }

  const initialValues: FormValuesProps = {
    price: venueProvider.price ? venueProvider.price : '',
    quantity: venueProvider.quantity ? Number(venueProvider.quantity) : '',
    isDuo: venueProvider.isDuo ?? false,
  }

  return (
    <div className={style['allocine-provider-parameters-container']}>
      <h4 className={style['title']}>Paramètres des offres synchronisées</h4>
      <div className={style['parameters-list']}>
        <div className={style['parameter-item']}>
          Prix de vente/place :{' '}
          <span>
            {venueProvider.price
              ? `${new Intl.NumberFormat('fr-FR', {
                  style: 'currency',
                  currency: 'EUR',
                }).format(venueProvider.price)}`
              : ''}
          </span>
        </div>
        <div className={style['parameter-item']}>
          Nombre de places/séance :{' '}
          <span>
            {`${
              typeof venueProvider.quantity === 'number'
                ? venueProvider.quantity
                : 'Illimité'
            }`}
          </span>
        </div>
        <div className={style['parameter-item']}>
          Accepter les offres DUO :{' '}
          <span>{`${venueProvider.isDuo ? 'Oui' : 'Non'} `}</span>
        </div>
      </div>
      <Button
        className={style['edit-parameters-btn']}
        variant={ButtonVariant.SECONDARY}
        onClick={openFormDialog}
      >
        Modifier les paramètres
      </Button>
      {isOpenedFormDialog && (
        <AllocineProviderFormDialog
          initialValues={initialValues}
          onCancel={closeFormDialog}
          onConfirm={onConfirmDialog}
          providerId={venueProvider.provider.id}
          venueId={venueProvider.venueId}
          offererId={offererId}
        />
      )}
    </div>
  )
}
