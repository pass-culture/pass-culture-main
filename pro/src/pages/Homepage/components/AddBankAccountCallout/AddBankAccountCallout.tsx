import { useAnalytics } from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

import styles from '../../Homepage.module.scss'

export const AddBankAccountCallout = () => {
  const { logEvent } = useAnalytics()

  return (
    <div className={styles['reimbursements-banner']}>
      <Banner
        title="Aucun compte bancaire configuré pour percevoir vos remboursements"
        variant={BannerVariants.ERROR}
        actions={[
          {
            href: '/administration/remboursements/informations-bancaires',
            label: 'Ajouter un compte bancaire',
            type: 'link',
            icon: fullNextIcon,
            onClick: () => {
              logEvent(BankAccountEvents.CLICKED_ADD_BANK_ACCOUNT)
            },
          },
        ]}
      />
    </div>
  )
}
