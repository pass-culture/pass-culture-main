import type { GetCollectiveOfferCollectiveStockResponseModel } from '@/apiClient/v1'
import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from '@/commons/utils/date'
import { TOTAL_PRICE_LABEL } from '@/pages/CollectiveOffer/CollectiveOfferStock/components/OfferEducationalStock/constants/labels'
import { Divider } from '@/ui-kit/Divider/Divider'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import { DEFAULT_RECAP_VALUE } from './constants'
import { formatDateTime } from './utils/formatDatetime'

export interface CollectiveOfferStockSectionProps {
  stock?: GetCollectiveOfferCollectiveStockResponseModel | null
  venueDepartmentCode?: string | null
}

export const CollectiveOfferStockSection = ({
  stock,
  venueDepartmentCode,
}: CollectiveOfferStockSectionProps) => {
  return (
    <>
      <SummaryDescriptionList
        descriptions={[
          {
            title: 'Date de début',
            text: stock?.startDatetime
              ? formatDateTime(
                  stock.startDatetime,
                  FORMAT_DD_MM_YYYY,
                  venueDepartmentCode
                )
              : DEFAULT_RECAP_VALUE,
          },
          {
            title: 'Date de fin',
            text: stock?.endDatetime
              ? formatDateTime(
                  stock.endDatetime,
                  FORMAT_DD_MM_YYYY,
                  venueDepartmentCode
                )
              : DEFAULT_RECAP_VALUE,
          },
          {
            title: 'Horaire',
            text:
              (stock?.startDatetime &&
                formatDateTime(
                  stock.startDatetime,
                  FORMAT_HH_mm,
                  venueDepartmentCode
                )) ||
              DEFAULT_RECAP_VALUE,
          },
          {
            title: 'Nombre de participants',
            text: stock?.numberOfTickets || DEFAULT_RECAP_VALUE,
          },
          { title: TOTAL_PRICE_LABEL, text: `${stock?.price}€` },
          {
            title: 'Informations sur le prix',
            text: stock?.educationalPriceDetail || DEFAULT_RECAP_VALUE,
          },
        ]}
      />
      <Divider size="large" />
      <SummarySubSection
        title="Conditions de réservation"
        shouldShowDivider={false}
      >
        <SummaryDescriptionList
          descriptions={[
            {
              title: 'Date limite de réservation',
              text: stock?.bookingLimitDatetime
                ? formatDateTime(
                    stock.bookingLimitDatetime,
                    FORMAT_DD_MM_YYYY,
                    venueDepartmentCode
                  )
                : DEFAULT_RECAP_VALUE,
            },
          ]}
        />
      </SummarySubSection>
    </>
  )
}
