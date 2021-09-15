import "./AppLayout.scss"
import * as React from "react"

import { Role } from "utils/types"

import { ReactComponent as Logo } from "../assets/logo.svg"

import { OffersSearch } from "./components/OffersSearch/OffersSearch"

export const AppLayout = ({ userRole }: { userRole: Role }): JSX.Element => (
  <>
    <header>
      <Logo />
    </header>
    <main className="app-layout">
      <OffersSearch userRole={userRole} />
    </main>
  </>
)
