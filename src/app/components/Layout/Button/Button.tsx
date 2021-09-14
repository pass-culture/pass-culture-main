import "./Button.scss"
import React from "react"

export const Button = ({
  onClick,
  text,
  isSubmit,
}: {
  onClick: () => void;
  text: string;
  isSubmit: boolean;
}): JSX.Element => (
  <button
    className="primary-button"
    onClick={onClick}
    type={isSubmit ? "submit" : "button"}
  >
    {text}
  </button>
)
