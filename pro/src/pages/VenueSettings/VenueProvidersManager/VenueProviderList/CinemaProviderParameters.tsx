import React, { useState } from 'react'

import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Button } from 'ui-kit/index'

import { CinemaProviderFormDialog } from './CinemaProviderFormDialog'
import style from './CinemaProviderParameters.module.scss'
import { CinemaProviderParametersValues } from './types'

interface CinemaProviderParametersProps {
  venueProvider: VenueProviderResponse
  afterVenueProviderEdit: (editedVenueProvider: VenueProviderResponse) => void
  offererId: number
}

export const CinemaProviderParameters = ({
  venueProvider,
  afterVenueProviderEdit,
  offererId,
}: CinemaProviderParametersProps): JSX.Element => {
  const [isOpenedFormDialog, setIsOpenedFormDialog] = useState(false)
  const notification = useNotification()

  const editVenueProvider = async (
    payload: CinemaProviderParametersValues
  ): Promise<boolean> => {
    try {
      const editedVenueProvider = await api.updateVenueProvider(payload)

      afterVenueProviderEdit(editedVenueProvider)
      notification.success(
        "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
      )
      return true
    } catch (error) {
      notification.error('Une erreur s’est produite, veuillez réessayer')
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
    payload: CinemaProviderParametersValues
  ): Promise<boolean> => {
    const isSuccess = await editVenueProvider({
      ...payload,
      isActive: venueProvider.isActive,
    })

    closeFormDialog()
    return isSuccess
  }

  const initialValues = {
    isDuo: venueProvider.isDuo,
  }

  return (
    <div className={style['cinema-provider-parameters']}>
      <h4 className={style['title']}>Paramètres des offres synchronisées</h4>
      <div className={style['cinema-provider-parameters-list']}>
        <div>
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
        <CinemaProviderFormDialog
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
