import type { GetVenuePricingPointResponseModel } from '@/apiClient/v1'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './PricingPoint.module.scss'

export interface PricingPointProps {
  venuePricingPoint: GetVenuePricingPointResponseModel
}
export const PricingPoint = ({
  venuePricingPoint,
}: Readonly<PricingPointProps>) => {
  return (
    <div className={styles['dropdown-container']}>
      <div className={styles['select']}>
        <Select
          disabled
          data-testid={'pricingPointSelect'}
          label="Structure avec SIRET utilisée pour le calcul de votre barème de remboursement"
          name="venueSiret"
          options={[
            {
              value: venuePricingPoint.id.toString(),
              label: `${venuePricingPoint.venueName} - ${venuePricingPoint.siret}`,
            },
          ]}
          value={venuePricingPoint.id.toString()}
        />
      </div>
    </div>
  )
}
