// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom"
import fetch from "jest-fetch-mock"
require("jest-fetch-mock").enableMocks()

global.fetch = fetch
require('dotenv').config({
  path: '.env.test',
})
