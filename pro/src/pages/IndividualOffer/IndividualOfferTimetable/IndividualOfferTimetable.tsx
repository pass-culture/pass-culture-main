import { useNavigate } from 'react-router'

import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { IndividualOfferLayout } from '@/components/IndividualOfferLayout/IndividualOfferLayout'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { StocksCalendar } from './components/StocksCalendar/StocksCalendar'

export const IndividualOfferTimetable = (): JSX.Element | null => {
  const { offer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const navigate = useNavigate()

  if (!offer?.priceCategories) {
    return <Spinner />
  }

  if (!offer.isEvent) {
    navigate('/404')
  }

  return (
    <IndividualOfferLayout offer={offer}>
      <StocksCalendar offer={offer} mode={mode} />
    </IndividualOfferLayout>
  )
}

// Below exports are used by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferTimetable
