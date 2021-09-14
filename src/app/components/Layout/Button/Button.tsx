import "./Button.scss"
import React from "react"

export const Button = ({
  onClick,
  text,
  type,
}: {
  onClick: () => void;
  text: string;
  type: "submit" | "reset" | "button" | undefined;
}): JSX.Element => (
  <button
    className="primary-button"
    onClick={onClick}
    type={type}
  >
    {text}
  </button>
)
