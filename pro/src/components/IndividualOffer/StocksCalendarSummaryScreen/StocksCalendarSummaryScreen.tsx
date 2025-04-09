import { GetIndividualOfferWithAddressResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { isOfferDisabled } from 'commons/core/Offers/utils/isOfferDisabled'
import { StocksCalendar } from 'components/IndividualOffer/StocksEventCreation/StocksCalendar/StocksCalendar'
import { getStockWarningText } from 'components/IndividualOffer/SummaryScreen/StockSection/StockSection'
import { getDepartmentCode } from 'components/IndividualOffer/utils/getDepartmentCode'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { SummarySection } from 'components/SummaryLayout/SummarySection'
import { Callout } from 'ui-kit/Callout/Callout'

type StocksCalendarSummaryScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}

export function StocksCalendarSummaryScreen({
  offer,
}: StocksCalendarSummaryScreenProps) {
  const editLink = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.STOCKS,
    mode: OFFER_WIZARD_MODE.EDITION,
  })

  return (
    <SummarySection
      title="Calendrier"
      editLink={editLink}
      aria-label="Modifier le calendrier"
    >
      {getStockWarningText(offer)}

      {!isOfferDisabled(offer.status) && (
        <Callout
          links={[
            {
              href: 'https://aide.passculture.app/hc/fr/articles/4411992053649--Acteurs-Culturels-Comment-annuler-ou-reporter-un-%C3%A9v%C3%A9nement-',
              label: 'Comment reporter ou annuler un évènement ?',
              isExternal: true,
            },
          ]}
        >
          Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne
          peuvent pas le faire à moins de 48h de l’évènement. Vous pouvez
          annuler un évènement en supprimant la ligne de stock associée. Cette
          action est irréversible.
        </Callout>
      )}

      <StocksCalendar
        offer={offer}
        departmentCode={getDepartmentCode(offer)}
        readonly
      />
    </SummarySection>
  )
}
