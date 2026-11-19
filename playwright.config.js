// @ts-check
const { defineConfig, devices } = require("@playwright/test");
const path = require("path");

const PYTHON = path.join(__dirname, ".venv", "Scripts", "python.exe");

module.exports = defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never", outputFolder: "e2e-report" }]],
  timeout: 60_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: "http://127.0.0.1:8000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    viewport: { width: 1280, height: 800 },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: `"${PYTHON}" manage.py runserver 127.0.0.1:8000 --noreload`,
    url: "http://127.0.0.1:8000",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  outputDir: "e2e-results",
});
