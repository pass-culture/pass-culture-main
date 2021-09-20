import "./AppLayout.scss"
import * as React from "react"
import { useCallback, useRef } from "react"

import { ReactComponent as Logo } from "assets/logo-with-text.svg"
import { Role, VenueFilterType } from "utils/types"

import {
  Notification,
  NotificationWrapper,
  NotificationRef,
} from "./components/Layout/Notification/Notification"
import { OffersSearch } from "./components/OffersSearch/OffersSearch"

export const AppLayout = ({
  userRole,
  removeVenueFilter,
  venueFilter,
}: {
  userRole: Role;
  removeVenueFilter: () => void;
  venueFilter: VenueFilterType | null;
}): JSX.Element => {
  const notificationRef = useRef<NotificationRef>()

  const notify = useCallback((notification: Notification) => {
    notificationRef.current?.notify(notification)
  }, [])

  return (
    <>
      <header>
        <Logo />
      </header>
      <main className="app-layout">
        {notify && (
          <OffersSearch
            notify={notify}
            removeVenueFilter={removeVenueFilter}
            userRole={userRole}
            venueFilter={venueFilter}
          />
        )}
      </main>
      <NotificationWrapper ref={notificationRef} />
    </>
  )
}
