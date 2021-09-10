import "./AppLayout.scss"
import * as React from "react"

import { OffersSearch } from "./components/OffersSearch/OffersSearch"

const App = (): JSX.Element => (
  <>
    <header>
      <h1>
        pass Culture
      </h1>
    </header>
    <main className="app-layout">
      <OffersSearch />
    </main>
    <footer />
  </>
)

export default App
