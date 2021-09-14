import "./Offers.scss"
import React from "react"

import { ResultType } from "utils/types"

import Offer from "./Offer"

export const Offers = ({ results }: { results: ResultType[] }): JSX.Element => (
  <ul className="offers">
    {results.map((result) => (
      <Offer
        key={result.id.raw}
        result={result}
      />
    ))}
  </ul>
)

export default Offers
