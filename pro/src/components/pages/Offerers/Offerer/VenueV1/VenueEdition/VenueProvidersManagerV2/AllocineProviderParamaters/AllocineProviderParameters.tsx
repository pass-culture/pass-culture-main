import * as pcapi from 'repository/pcapi/pcapi'
import React, { useCallback, useState } from 'react'
import AllocineProviderFormDialog from '../../VenueProvidersManager/AllocineProviderFormDialog/AllocineProviderFormDialog'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { IAllocineProviderParametersValues } from './types'
import { IVenueProviderApi } from '../../VenueProvidersManager/CinemaProviderItem/types'
import style from './AllocineProviderParameters.module.scss'
import useNotification from 'components/hooks/useNotification'

export interface IAllocineProviderParametersProps {
  venueProvider: IVenueProviderApi
  afterVenueProviderEdit: (editedVenueProvider: IVenueProviderApi) => void
}

const AllocineProviderParameters = ({
  venueProvider,
  afterVenueProviderEdit,
}: IAllocineProviderParametersProps): JSX.Element => {
  const [isOpenedFormDialog, setIsOpenedFormDialog] = useState(false)
  const notification = useNotification()

  const editVenueProvider = useCallback(
    (payload: IAllocineProviderParametersValues) => {
      pcapi
        .editVenueProvider(payload)
        .then(editedVenueProvider => {
          afterVenueProviderEdit(editedVenueProvider)
          notification.success(
            "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
          )
        })
        .catch(() => {
          notification.error("Une erreur s'est produite, veuillez réessayer")
        })
    },
    [afterVenueProviderEdit]
  )

  const openFormDialog = useCallback(() => {
    setIsOpenedFormDialog(true)
  }, [])

  const closeFormDialog = useCallback(() => {
    setIsOpenedFormDialog(false)
  }, [])

  const onConfirmDialog = useCallback(
    (payload: IAllocineProviderParametersValues) => {
      payload = {
        ...payload,
        isActive: venueProvider.isActive,
      }
      editVenueProvider(payload)

      closeFormDialog()
    },
    [closeFormDialog, editVenueProvider]
  )

  const initialValues = {
    price: venueProvider.price,
    quantity: venueProvider.quantity,
    isDuo: venueProvider.isDuo,
  }

  return (
    <div className={style['allocine-provider-parameters-container']}>
      <h4 className={style['title']}>Paramètres des offres synchronisées</h4>
      <div className={style['parameters-list']}>
        <div className={style['parameter-item']}>
          Prix de vente/place :{' '}
          <span>
            {`${new Intl.NumberFormat('fr-FR', {
              style: 'currency',
              currency: 'EUR',
            }).format(venueProvider.price)}`}
          </span>
        </div>
        <div className={style['parameter-item']}>
          Nombre de places/séances :{' '}
          <span>
            {`${venueProvider.quantity ? venueProvider.quantity : 'Illimité'}`}
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
          // @ts-ignore
          initialValues={initialValues}
          onCancel={closeFormDialog}
          onConfirm={onConfirmDialog}
          providerId={venueProvider.providerId}
          venueId={venueProvider.venueId}
        />
      )}
    </div>
  )
}

export default AllocineProviderParameters
