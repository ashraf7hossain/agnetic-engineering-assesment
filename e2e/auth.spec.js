const { test, expect } = require("@playwright/test");
const { register, login, uid } = require("./helpers");

test.describe("Auth", () => {
  test("registers and lands on dashboard", async ({ page }) => {
    const id = uid();
    await register(page, {
      username: `u_${id}`,
      email: `u_${id}@example.com`,
      password: "DemoPass123!",
    });
    await expect(page.getByRole("heading", { name: "Your spaces" })).toBeVisible();
  });

  test("logs in existing user", async ({ page }) => {
    const id = uid();
    const user = {
      username: `login_${id}`,
      email: `login_${id}@example.com`,
      password: "DemoPass123!",
    };
    await register(page, user);
    await page.locator("header form button[type=submit]").click(); // logout
    await expect(page.getByRole("link", { name: "Log in" }).first()).toBeVisible();
    await login(page, user);
    await expect(page.getByRole("heading", { name: "Your spaces" })).toBeVisible();
  });

  test("password reset page renders", async ({ page }) => {
    await page.goto("/accounts/password_reset/");
    await expect(page.getByRole("heading", { name: /Reset password/i })).toBeVisible();
    await page.locator("#id_email").fill("someone@example.com");
    await page.locator("main form button[type=submit]").click();
    await expect(page.getByRole("heading", { name: /Check your inbox/i })).toBeVisible();
  });
});
