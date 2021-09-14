import "./AppLayout.scss"
import * as React from "react"

import { ReactComponent as Logo } from "../assets/logo.svg"

import { OffersSearch } from "./components/OffersSearch/OffersSearch"

export const AppLayout = (): JSX.Element => (
  <>
    <header>
      <Logo />
    </header>
    <main className="app-layout">
      <OffersSearch />
    </main>
  </>
)
