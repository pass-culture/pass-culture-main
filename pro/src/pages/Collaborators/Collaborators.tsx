/* istanbul ignore file */

// Component only for display (sub-components already tested)

import { useSelector } from 'react-redux'

import { AppLayout } from 'app/AppLayout'
import { AttachmentInvitations } from 'pages/Offerers/Offerer/OffererDetails/AttachmentInvitations/AttachmentInvitations'
import { selectCurrentOffererId } from 'store/user/selectors'

export const Collaborators = (): JSX.Element | null => {
  const currentOffererId = useSelector(selectCurrentOffererId)

  if (!currentOffererId) {
    return null
  }

  return (
    <AppLayout>
      <h1>Collaborateurs</h1>

      <AttachmentInvitations offererId={currentOffererId} />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Collaborators
