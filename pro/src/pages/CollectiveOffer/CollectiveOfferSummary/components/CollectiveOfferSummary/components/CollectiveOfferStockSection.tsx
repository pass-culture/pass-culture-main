import type {
  CollectiveAdditionalFeeResponseModel,
  GetCollectiveOfferCollectiveStockResponseModel,
} from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from '@/commons/utils/date'
import { TOTAL_PRICE_LABEL } from '@/pages/CollectiveOffer/CollectiveOfferStock/components/OfferEducationalStock/constants/labels'
import { Divider } from '@/ui-kit/Divider/Divider'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import styles from './CollectiveOfferStockSection.module.scss'
import { DEFAULT_RECAP_VALUE } from './constants'
import { formatDateTime } from './utils/formatDatetime'

export interface CollectiveOfferStockSectionProps {
  stock?: GetCollectiveOfferCollectiveStockResponseModel | null
  venueDepartmentCode?: string | null
}

const getDateText = (
  datetime: string | null | undefined,
  venueDepartmentCode: string | null | undefined,
  format: string = FORMAT_DD_MM_YYYY
) =>
  datetime
    ? formatDateTime(datetime, format, venueDepartmentCode)
    : DEFAULT_RECAP_VALUE

export const CollectiveOfferStockSection = ({
  stock,
  venueDepartmentCode,
}: CollectiveOfferStockSectionProps) => {
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  const oldStockDescriptions = [
    {
      title: 'Date de début',
      text: getDateText(stock?.startDatetime, venueDepartmentCode),
    },
    {
      title: 'Date de fin',
      text: getDateText(stock?.endDatetime, venueDepartmentCode),
    },
    {
      title: 'Horaire',
      text: getDateText(
        stock?.startDatetime,
        venueDepartmentCode,
        FORMAT_HH_mm
      ),
    },
    {
      title: 'Nombre de participants',
      text: stock?.numberOfTickets || DEFAULT_RECAP_VALUE,
    },
    { title: TOTAL_PRICE_LABEL, text: `${stock?.price}€` },
    {
      title: 'Informations sur le prix',
      text: stock?.priceDetail || DEFAULT_RECAP_VALUE,
    },
  ]

  const oldBookingLimitDescriptions = [
    {
      title: 'Date limite de réservation',
      text: getDateText(stock?.bookingLimitDatetime, venueDepartmentCode),
    },
  ]

  const dateDescriptions = [
    {
      title: 'Date de début',
      text: getDateText(stock?.startDatetime, venueDepartmentCode),
    },
    {
      title: 'Date de fin',
      text: getDateText(stock?.endDatetime, venueDepartmentCode),
    },
    {
      title: 'Horaire',
      text: getDateText(
        stock?.startDatetime,
        venueDepartmentCode,
        FORMAT_HH_mm
      ),
    },
  ]

  const bookingLimitDescriptions = [
    {
      text: getDateText(stock?.bookingLimitDatetime, venueDepartmentCode),
    },
  ]

  const participantsDescriptions = [
    {
      title: "Nombre d'élèves",
      text: stock?.numberOfTickets || DEFAULT_RECAP_VALUE,
    },
    {
      title: "Nombre d'accompagnateurs",
      text: stock?.numberOfTeachers ?? DEFAULT_RECAP_VALUE,
    },
  ]

  const priceDescriptions = [
    {
      title: 'Tarif de la prestation',
      text:
        stock?.servicePrice === null || stock?.servicePrice === undefined
          ? DEFAULT_RECAP_VALUE
          : `${stock.servicePrice}€`,
    },
    {
      title: 'Frais annexes',
      text: (stock?.collectiveAdditionalFees?.length ?? 0) > 0 ? 'Oui' : 'Non',
    },
    ...((stock?.collectiveAdditionalFees?.length ?? 0) > 0
      ? [
          {
            title: 'Type de frais annexe',
            text: (
              <ul className={styles['additional-fees-list']}>
                {stock?.collectiveAdditionalFees?.map(
                  (fee: CollectiveAdditionalFeeResponseModel) => (
                    <li key={`${fee.type}-${fee.label}`}>
                      {fee.label || fee.type} - {fee.amount}€
                    </li>
                  )
                )}
              </ul>
            ),
          },
        ]
      : []),
    {
      title: 'Prix total TTC',
      text:
        stock?.price === null || stock?.price === undefined
          ? DEFAULT_RECAP_VALUE
          : `${stock.price}€`,
    },
  ]

  if (!isNewCollectivePriceEnabled) {
    return (
      <>
        <SummaryDescriptionList descriptions={oldStockDescriptions} />
        <Divider size="large" />
        <SummarySubSection
          title="Conditions de réservation"
          shouldShowDivider={false}
        >
          <SummaryDescriptionList descriptions={oldBookingLimitDescriptions} />
        </SummarySubSection>
      </>
    )
  }

  return (
    <>
      <SummarySubSection title="Date et heure" shouldShowDivider={false}>
        <SummaryDescriptionList descriptions={dateDescriptions} />
      </SummarySubSection>
      <SummarySubSection
        title="Date limite de réservation"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList descriptions={bookingLimitDescriptions} />
      </SummarySubSection>
      <SummarySubSection
        title="Nombre de participants"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList descriptions={participantsDescriptions} />
      </SummarySubSection>
      <SummarySubSection title="Prix de votre offre" shouldShowDivider>
        <SummaryDescriptionList descriptions={priceDescriptions} />
      </SummarySubSection>
    </>
  )
}
