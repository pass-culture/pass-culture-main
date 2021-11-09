import "./AppLayout.scss"
import * as React from "react"

import { ReactComponent as Logo } from "assets/logo-with-text.svg"
import { Role, VenueFilterType } from "utils/types"

import { OffersSearch } from "./components/OffersSearch/OffersSearch"

export const AppLayout = ({
  userRole,
  removeVenueFilter,
  venueFilter,
}: {
  userRole: Role;
  removeVenueFilter: () => void;
  venueFilter: VenueFilterType | null;
}): JSX.Element => (
  <>
    <header>
      <Logo />
    </header>
    <main className="app-layout">
      <OffersSearch
        removeVenueFilter={removeVenueFilter}
        userRole={userRole}
        venueFilter={venueFilter}
      />
    </main>
  </>
)
