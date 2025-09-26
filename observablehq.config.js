// See https://observablehq.com/framework/config for documentation.
export default {
  // The app's title; used in sidebar and webpage titles.
  title: "bhs-observability",

  // The pages and sections in the sidebar. If you don't specify this option,
  // all pages will be listed in alphabetical order. Listing pages explicitly
  // lets you organize them into sections and have unlisted pages.
  pages: [
    {
      name: "Dashboards",
      pages: [
        {name: "Home", path: "/"},
        {name: "Live Dashboard", path: "/live-dashboard"},
        {name: "Realtime Dashboard", path: "/realtime-dashboard"},
        {name: "Merged Live Dashboard", path: "/merged-live-dashboard"},
        {name: "Today's View", path: "/todays-view"},
        {name: "Test Dashboard", path: "/test-dashboard"},
        {name: "Database Dashboard", path: "/database-dashboard"},
        {name: "Example Dashboard", path: "/example-dashboard"}
      ]
    },
    {
      name: "Machine Data",
      pages: [
        {name: "Mazak VTC 200", path: "/mazak-vtc200"},
        {name: "Mazak VTC 300", path: "/mazak-vtc300-final"},
        {name: "Mazak 350MSY", path: "/mazak-350msy"}
      ]
    },
    {
      name: "Reports",
      pages: [
        {name: "Example Report", path: "/example-report"}
      ]
    },
    {
      name: "Documentation",
      pages: [
        {name: "Component Examples", path: "/component-examples"},
        {name: "Dashboard Styles", path: "/DASHBOARD_STYLES_README.md"}
      ]
    }
  ],

  // Content to add to head of page, e.g. for a favicon:
  head: '<link rel="icon" href="observable.png" type="image/png" sizes="32x32">',

  // The path to source root.
  root: "src",

  // Some additional configuration options and their defaults:
  // theme: "default", // try "light", "dark", "slate", etc.
  // header: "", // what to show in header (HTML)
  // footer: "Built with Observable.", // what to show in footer (HTML)
  // sidebar: true, // whether to show sidebar
  // toc: true, // whether to show table of contents
  // pager: true, // whether to show previous & next links in footer
  // output: "dist", // path to output root for build
  // search: true, // activate search
  // linkify: true, // convert URLs in Markdown to links
  // typographer: false, // smart quotes and other typographic improvements
  // preserveExtension: false, // drop .html from URLs
  // preserveIndex: false, // drop /index from URLs
};
