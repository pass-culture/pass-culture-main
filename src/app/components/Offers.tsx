import React from "react"

import { ResultType } from "utils/types"

import Offer from "./Offer"

export const Offers = ({ results }: { results: ResultType[] }): JSX.Element => (
  <div>
    {results.map((result) => (
      <Offer
        key={result.id.raw}
        result={result}
      />
    ))}
  </div>
)

export default Offers
