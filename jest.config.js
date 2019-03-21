module.exports = {
  collectCoverageFrom: [
    // "**/*.{js,jsx}",
    '<rootDir>/src/**.{js,jsx}',
    // "!**/node_modules/**",
    '!<rootDir>/node_modules/',
    '!<rootDir>/build/',
  ],
  moduleFileExtensions: ['web.js', 'js', 'json', 'web.jsx', 'jsx', 'node'],
  moduleNameMapper: {
    '^react-native$': 'react-native-web',
  },
  setupFiles: ['<rootDir>/jest-polyfill.js', '<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom-global',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx}',
    '<rootDir>/src/**/?(*.)(spec|test).{js,jsx}',
    '**/?(*.)+(spec).js?(x)',
  ],
  testURL: 'http://localhost',
  transform: {
    '^.+\\.(js|jsx)$': '<rootDir>/node_modules/babel-jest',
    '^.+\\.js$': 'babel-jest',
  },
  transformIgnorePatterns: [
    '<rootDir>/node_modules/',
    '[/\\\\]node_modules[/\\\\].+\\.(js|jsx)$',
  ],
  verbose: true,
}
