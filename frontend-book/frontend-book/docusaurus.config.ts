import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'ROS 2 Educational Module',
  tagline: 'Learn ROS 2 fundamentals for Physical AI and Humanoid Systems',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://Uzmakanwl.github.io', // Replace with your project's URL
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub Pages, this is usually '/<project-name>/'
  baseUrl: '/frontend-book/',

  // GitHub pages deployment config.
  organizationName: 'Uzmakanwl', // Usually your GitHub org/user name.
  projectName: 'physical-humaiod-book', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  markdown: {
    format: 'mdx',
    mermaid: false,
  },

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.ts'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/Uzmakanwl/physical-humaiod-book/tree/main/',
        },
        blog: false, // Disable blog for educational module
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'ROS 2 Educational Module',
        logo: {
          alt: 'ROS 2 Logo',
          src: 'img/logo.svg', // Add your logo if available
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Module 1',
          },
          {
            href: 'https://github.com/Uzmakanwl/physical-humaiod-book',
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
                label: 'Module 1 - ROS 2 Fundamentals',
                to: '/docs/module-1-ros2-fundamentals',
              },
              {
                label: 'Module 2 - Digital Twin (Gazebo & Unity)',
                to: '/docs/module-2-digital-twin',
              },
              {
                label: 'Module 3 - The AI-Robot Brain (NVIDIA Isaac™)',
                to: '/docs/module-3-nvidia-isaac',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Stack Overflow',
                href: 'https://stackoverflow.com/questions/tagged/ros2',
              },
              {
                label: 'ROS Answers',
                href: 'https://answers.ros.org/questions/',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/Uzmakanwl/physical-humaiod-book',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} ROS 2 Educational Module. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'json', 'yaml'],
      },
    }),
};

export default config;