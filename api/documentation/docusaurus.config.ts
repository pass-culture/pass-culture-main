import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import type * as Redocusaurus from 'redocusaurus';

const getOpenAPIJsonUrlFromEnv = (): string => {
  const env = process.env['ENV'];

  // TO DO: update once the proper devops config is available.
  if (env === 'deploy') {
    return 'https://backend.testing.passculture.team/openapi.json';
  }

  return 'http://localhost/openapi.json';
}


const getDocumentationBaseUrlFromEnv = (): string => {
  const env = process.env['ENV'];

  // TO DO: update once the proper devops config is available.
  if (env === 'deploy') {
    return 'https://pass-culture.github.io';
  }

  return 'http://localhost:3000';
}

const config: Config = {
  title: 'Pass Culture documentation',
  tagline: '',
  favicon: 'img/favicon.ico',

  // TO DO: update once the proper devops config is available.
  url: getDocumentationBaseUrlFromEnv(),
  baseUrl: '/pass-culture-api-documentation/',
  organizationName: 'pass-culture',
  projectName: 'pass-culture-api-documentation',
  deploymentBranch: 'gh-pages',
  // End TODO

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  trailingSlash: false,
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
    // Redocusaurus config
    [
      'redocusaurus',
      {
        specs: [
          {
            spec: getOpenAPIJsonUrlFromEnv(),
            route: '/rest-api/',
          },
        ],
        theme: {
          primaryColor: '#6123df',
        },
      },
    ] satisfies Redocusaurus.PresetEntry,
  ],

  themeConfig: {
    image: 'img/pass-culture-social-card.jpg',
    colorMode: {
      disableSwitch: true,
    },
    navbar: {
      title: 'Pass Culture Developers',
      logo: {
        alt: 'Pass Culture Logo',
        src: 'img/passculture_logo.jpeg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'REST API',
          href: '/rest-api/',
        },
        {
          to: '/change-logs',
          label: 'Change logs',
          position: 'left',
        },
        {
          href: 'https://github.com/pass-culture/pass-culture-main',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Documentation',
              to: '/docs/category/mandatory-steps',
            },
            {
              label: 'REST API',
              to: '/rest-api',
            },
            {
              label: 'Change logs',
              to: '/change-logs',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'X',
              href: 'https://x.com/pass_Culture',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/pass-culture/pass-culture-main',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Pass Culture. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
