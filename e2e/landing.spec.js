const { test, expect } = require("@playwright/test");

test.describe("Landing", () => {
  test("shows brand and CTAs", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("link", { name: "Testify" }).first()).toBeVisible();
    await expect(
      page.getByRole("heading", { name: /Collect customer love/i })
    ).toBeVisible();
    await expect(page.getByRole("link", { name: "Start free" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Sign up" })).toBeVisible();
  });

  test("sign up CTA goes to register", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Start free" }).click();
    await expect(page).toHaveURL(/\/accounts\/register\/?/);
  });
});
