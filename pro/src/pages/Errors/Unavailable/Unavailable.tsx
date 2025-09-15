import { ErrorLayout } from '@/app/App/layouts/ErrorLayout/ErrorLayout'
import strokeWipIcon from '@/icons/stroke-wip.svg'

export const Unavailable = () => {
  return (
    <ErrorLayout
      mainHeading="Page indisponible"
      paragraph="Veuillez rééssayer plus tard"
      errorIcon={strokeWipIcon}
    />
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Unavailable
