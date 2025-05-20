import { GetOffererResponseModel } from 'apiClient/v1'
import { useActiveStep } from 'commons/hooks/useActiveStep'
import { Tag, TagVariant } from 'design-system/Tag/Tag'
import fullErrorIcon from 'icons/full-error.svg'
import { NavLinkItem, NavLinkItems } from 'ui-kit/NavLinkItems/NavLinkItems'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import {
  STEP_ID_BANK_INFORMATIONS,
  STEP_ID_INCOMES,
  STEP_ID_INVOICES,
  STEP_NAMES,
} from './constants'
import styles from './ReimbursementsTabs.module.scss'

type ReimbursementsTabsProps = {
  selectedOfferer: GetOffererResponseModel | null
}

export const ReimbursementsTabs = ({
  selectedOfferer,
}: ReimbursementsTabsProps) => {
  const activeStep = useActiveStep(STEP_NAMES)
  const hasWarning =
    (selectedOfferer &&
      (selectedOfferer.venuesWithNonFreeOffersWithoutBankAccounts.length > 0 ||
        selectedOfferer.hasBankAccountWithPendingCorrections)) ??
    false

  const getSteps = () => {
    const steps = [
      {
        id: STEP_ID_INVOICES,
        label: 'Justificatifs',
        url: '/remboursements',
      },
      {
        id: STEP_ID_BANK_INFORMATIONS,
        label: (
          <>
            Informations bancaires
            {hasWarning && (
              <SvgIcon
                src={fullErrorIcon}
                alt="Une action est requise dans cet onglet"
                width="20"
                className={styles['error-icon']}
              />
            )}
          </>
        ),
        url: '/remboursements/informations-bancaires',
      },
      {
        id: STEP_ID_INCOMES,
        label: (
          <div className={styles['label-with-tag']}>
            Chiffre d’affaires&nbsp;
            <Tag label="Nouveau" variant={TagVariant.NEW} />
          </div>
        ),
        url: '/remboursements/revenus',
      },
    ]

    return steps
  }

  const tabs: NavLinkItem[] = getSteps().map(({ id, label, url }) => ({
    key: id,
    label,
    url,
  }))

  return (
    <NavLinkItems
      links={tabs}
      selectedKey={activeStep}
      navLabel="Sous menu - gestion financière"
    />
  )
}
