import { Offerer, Venue } from 'core/Offers/types'
import Icon from 'components/layout/Icon'
import PricingPoint from '../PricingPoint/PricingPoint'
import React from 'react'
import ReimbursementPoint from '../ReimbursementPoint/ReimbursementPoint'

import styles from './ReimbursementFields.module.scss'

export interface ReimbursementInterface {
  offerer: Offerer
  readOnly: boolean
  scrollToSection?: boolean
  venue: Venue
}

const ReimbursementFields = ({
  offerer,
  readOnly,
  scrollToSection,
  venue,
}: ReimbursementInterface) => {
  return (
    <>
      <div className="section">
        <h2 className="main-list-title">
          Remboursement
          <a
            className={styles['reimbursement-hint']}
            href="todo"
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon svg={'ico-external-site-filled'} />
            En savoir plus sur les remboursements
          </a>
        </h2>
        <PricingPoint />
        <ReimbursementPoint
          offerer={offerer}
          readOnly={readOnly}
          scrollToSection={scrollToSection}
          venue={venue}
        />
      </div>
    </>
  )
}

export default ReimbursementFields
