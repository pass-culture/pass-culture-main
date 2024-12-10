import classNames from 'classnames'

import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'

import styles from './IndividualOffersTableHead.module.scss'

type IndividualOffersTableHeadProps = {
  areAllOffersSelected: boolean
  isAtLeastOneOfferChecked: boolean
  isRestrictedAsAdmin: boolean
  toggleSelectAllCheckboxes: () => void
}

export const IndividualOffersTableHead = ({
  areAllOffersSelected,
  isAtLeastOneOfferChecked,
  isRestrictedAsAdmin,
  toggleSelectAllCheckboxes,
}: IndividualOffersTableHeadProps): JSX.Element => {
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  return (
    <thead role="rowgroup" className={styles['individual-offers-thead']}>
      <tr>
        <th
          colSpan={1}
          role="columnheader"
          className={classNames(
            styles['individual-offers-thead-th'],
            styles['individual-offers-thead-th-checkbox']
          )}
        >
          <div className={styles['individual-offers-thead-th-checkbox-wrapper']}>
            <BaseCheckbox
              inputClassName={styles['individual-offers-thead-th-checkbox-input']}
              labelClassName={styles['individual-offers-thead-th-checkbox-label']}
              checked={areAllOffersSelected}
              partialCheck={
                !areAllOffersSelected && isAtLeastOneOfferChecked
              }
              disabled={isRestrictedAsAdmin}
              onChange={toggleSelectAllCheckboxes}
              label={
                areAllOffersSelected
                  ? 'Tout désélectionner'
                  : 'Tout sélectionner'
              }
            />
          </div>
        </th>
        <th role="columnheader" className={styles['individual-offers-thead-th']}>Nom de l’offre</th>
        <th role="columnheader" className={styles['individual-offers-thead-th']}>
          {offerAddressEnabled ? 'Localisation' : 'Lieu'}
        </th>
        <th role="columnheader" className={styles['individual-offers-thead-th']}>Stocks</th>
        <th role="columnheader" className={styles['individual-offers-thead-th']}>Statut</th>
        <th
          role="columnheader"
          className={classNames(
            styles['individual-offers-thead-th'],
            styles['individual-offers-thead-th-actions']
          )}
        >
          Actions
        </th>
      </tr>
    </thead>
  )
}
